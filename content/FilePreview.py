import re
import urllib

from Products.ATContentTypes.content.base import *
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr
from Products.Archetypes import transaction

from os.path import splitext, basename

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent

from AccessControl import ClassSecurityInfo

from Products.ARFilePreview.config import PROJECTNAME
from Products.ARFilePreview.interfaces import IFilePreview


from SubMapper import SubMapper

FilePreviewSchema = Schema(
  (
    FileField('OriginalFile',
        primary=1,
        required=1,
        widget=FileWidget(
            i18n_domain = "filepreview",
            description = "Select the file to be added by clicking the 'Browse' button.",
            description_msgid = "desc_origfile",
            label= "File",
            label_msgid = "label_file",
            show_content_type = False,
        )
    ),
    TextField('HTMLPreview',
        default='',
        searchable=1,
        widget=TextAreaWidget(label='Previsualisation',
            visible ={'edit': 'invisible','view': 'invisible'}
        ),
        allowed_content_types= ('text/html',),
        default_output_type = 'text/html',
    ),
  )
) + ATContentTypeSchema.copy() + Schema( marshall=PrimaryFieldMarshaller() )

FilePreviewSchema['title'].required=0
#FilePreviewSchema['allowDiscussion'].widget.visible={'edit': 'visible', 'view': 'invisible', 'metadata': 'invisible'}


class FilePreview(ATCTContent, HistoryAwareMixin):
    """A special content-type to store binary document along with an html preview."""
    #Its content is converted to html and stored as html and binary.
    #The file's content is fully indexed
    __implements__ = ATCTContent.__implements__ + \
                     HistoryAwareMixin.__implements__ + \
                     (IFilePreview,)
    portal_type = meta_type = "FilePreview"
    archetype_name = "File Preview"
    i18n_domain = "filepreview"
    typeDescription= 'A special content-type to store binary document along with an html preview.'
    typeDescMsgId  = 'description_edit_filepreview'
    schema = FilePreviewSchema

    security       = ClassSecurityInfo()
    actions = updateActions(ATCTContent, HistoryAwareMixin.actions )
    
    _at_rename_after_creation = False
    
    _v_changedfile = True
    
    def __bobo_traverse__(self, REQUEST, name):
        '''transparent access to document subobjects
        '''
        if (not hasattr(self,"document_subobjects")) or (self.document_subobjects is None) or (not (name in self.document_subobjects.keyz())):
            return ATCTContent.__bobo_traverse__(self, REQUEST, name)
        try:
            submapper = self.document_subobjects
        except AttributeError:
            data = None
        else:
            data = submapper.__of__(self).traverse(name)
        if data is not None:
            return data
        else:
            # fallback
            return ATCTContent.__bobo_traverse__(self, REQUEST, name)    
    
    def updateFPTitle(self, newTitle=None, num=-1):
        """
        This method sets the title from the filename
        """
        if newTitle is None:
            newTitle=self.getOriginalFile().filename
        if num>=0:
            base, ext = splitext(newTitle)
            newTitle="%s-%02d%s"%(base, num, ext)
        newTitle = re.sub("[_-]"," ", newTitle)
        if newTitle!=unicode(self.Title(charset='utf-8'), 'utf-8'):
            self.setTitle(newTitle)
    
    def updateFPId(self, filename):
        """
        This method sets the id from the filename
        """
        plone_utils = getToolByName(self, 'plone_utils', None)
        if plone_utils is None or not shasattr(plone_utils, 'normalizeString'):
            return None
        new_id = plone_utils.normalizeString(filename)
        if 'portal_factory' in self.getPhysicalPath():
            container = self.aq_parent.aq_parent.aq_parent
        else:
            container = self.aq_parent
        num = -1
        if self.getId()!=new_id:
            if not container.checkIdAvailable(new_id):
                base, ext = tuple(splitext(new_id))
                while (self.getId()!=new_id) and (not container.checkIdAvailable(new_id)):
                    num+=1
                    new_id = "%s-%02d%s" % (base, num, ext)
            #the savepoint is mandatory for portal_factory
            transaction.savepoint(optimistic=True)
            self.setId(new_id)
        return new_id, num
    
    def updatePreview(self):
        """
        This method extracts a html preview from the file
        """
        #print "UPDATEPREVIEW"
##        if not self._v_changedfile:
##            return
##        self._v_changedfile=False
        
        #get original document
        file=self.getOriginalFile()
        
        if not hasattr(file, 'data'):
            return
        
        html_converted=''
        
        #get the full binary from file
        try:
            chunk=file.data
            inputdata=''
            while chunk is not None:
                inputdata+=chunk.data
                chunk=chunk.next
        except AttributeError:
            inputdata=file.data
        #convert to text/html
        transforms = getToolByName(self, 'portal_transforms')
        data=transforms.convertTo('text/html', inputdata, filename=file.filename)

        if data is None:
          self.setHTMLPreview(u"")
        else:
            #get the html code
            html_converted = data.getData()
            #update internal links
            #remove bad character '\xef\x81\xac' from HTMLPreview
            html_converted = re.sub('\xef\x81\xac', "", html_converted)
            # patch image sources since html base is that of our parent
            subobjs = data.getSubObjects()
            if len(subobjs)>0:
                self.document_subobjects = SubMapper( subobjs)
                html_converted = self.document_subobjects.__of__(self).map_it(html_converted)
            #html_converted=self.getitconverted(html_converted)
        #store the html in the HTMLPreview field for preview
        self.setHTMLPreview(html_converted.decode('utf-8'), mimetype='text/html')
        
    def post_validate(self, REQUEST, errors):
        """
        This method looks if the file is replaced by a new one. 
        In this case, the file is re-processed.
        """
        fieldset = REQUEST.form.get('fieldset', 'default')
        if fieldset == 'default':
          #if the REQUEST send us a file, replace the id with filename
          if REQUEST.get('OriginalFile_delete', "")!="nochange":
              self._v_changedfile=True
          else:
              self._v_changedfile=False
        
    # This method is only called once after object creation.
    def at_post_create_script(self):
        """
        This method is called after every filepreview creation.
        It triggers the conversion of the original file to text/html (updatePreview)
        and parse it for metadata (updateMetadata)
        """
        #print "POST_CREATE"
        if self._v_changedfile and bool(self.getOriginalFile()):
            filename=self.getOriginalFile().filename
            idobj, fnum = self.updateFPId(filename)
            self.getOriginalFile().filename = idobj
            self.updatePreview()
            if len(self.Title().strip())==0:
                self.updateFPTitle(newTitle=filename, num=fnum)
        self.reindexObject()
        
    def at_post_edit_script(self):
        """
        This method is called after every subsequent edit.
        It triggers the conversion of the original file to text/html (updatePreview)
        and parse it for metadata (updateMetadata)
        """
        #print "POST_EDIT"
        if self._v_changedfile and bool(self.getOriginalFile()):
            filename = self.getOriginalFile().filename
            idobj, fnum = self.updateFPId(filename)
            self.getOriginalFile().filename = idobj
            self.updateFPTitle(newTitle=filename, num = fnum)
            self._v_changedfile=False
        self.updatePreview()
        self.reindexObject()
        
        
    security.declarePrivate('manage_afterPUT')
    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,
        filename, REQUEST, RESPONSE):
        """
        This method is called after a FTP/WebDAV PUT has been marshalled.
        """
        self._v_changedfile=True
        filename = unicode(urllib.unquote(REQUEST._steps[-2]).decode('utf-8','ignore'))
        idobj, fnum = self.updateFPId(filename)
        self.getOriginalFile().filename=idobj
        ##self.updateFPTitle(newTitle=filename, num = fnum)
        self.updatePreview()
        self.reindexObject()
        ATCTContent.manage_afterPUT(self,data,marshall_data,file,context,mimetype,filename,REQUEST,RESPONSE)
        
registerATCT(FilePreview,PROJECTNAME)
