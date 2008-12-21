# -*- coding: utf-8 -*-

from five import grok
from atreal.speed.content import interfaces as speed
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from interfaces import IMetaGetter


class MetadataExtractor(grok.Adapter):
    grok.context(speed.ISpeedFile)
    grok.implements(speed.IMetadataExtractor)

    @property
    def filename(self):
        return self.context.getFile().filename

    def updateMetadata(self):
        file = self.context.getFile()
        metagetter = queryUtility(IMetaGetter, name=file.content_type)

        if metagetter is None:
            inputdata=None
            
        elif metagetter.html_preview:
            inputdata = self.context.getHTMLPreview()
            
        else:
            try:
                chunk=file.data
                origdata=''
                while chunk is not None:
                    origdata+=chunk.data
                    chunk=chunk.next
            except AttributeError:
                origdata = file.data
    
        transforms = getToolByName(self.context,'portal_transforms')
        try:
            inputdata = transforms.convertTo(metagetter.output,
                                             origdata,
                                             filename = file.filename).getData()
        except Exception, e:
            print "meta.py setmetas(%s) : %s" % (file.filename, str(e))
            inputdata=None

        if inputdata is not None:
            values = metagetter(inputdata)
        else:
            values={}

        try:
            form = self.context.REQUEST.form
        except AttributeError:
            form = {}
            

        string_metas = ['Contexte', 'Sujet', 'Reference', 'AuteurCreation', 'AuteurModification', 'Version', 'Valideurs']
        date_metas = ['DateCreation', 'DateModification', 'DateValidation']
        for key, value in values.iteritems():
            if not key in form:
                if key in string_metas:
                    self.context.getField(key).set(self.context, converthtml(value))
                elif key in date_metas:
                    tmpdate = tozopedate(value)
                    self.context.getField(key).set(self.context, tmpdate)
                else:
                    print '*** Unaccounted meta field?', key, value


    def updateTitleFromMetas(self, num=-1):
        """This method sets the title from the metadata
        """
        newTitle = self.filename
        if len(self.context.getSujet())>0:
            newTitle=self.context.getSujet()
        elif (self.context.description!=None) and (len(self.context.description)>0):
            newTitle=self.context.Description
        else:
            if newTitle is None:
                newTitle=self.context.getOriginalFile().filename
            if num>=0:
                base, ext = splitext(newTitle)
                newTitle="%s-%02d%s"%(base, num, ext)
            newTitle = re.sub("[_-]"," ", newTitle)
        
        if newTitle!=self.context.Title:
            self.context.update(title=newTitle)
    
    
    def updateAydi(self):
        """This method sets the id from the filename
        """
        filename = self.filename
        new_id = normalizeString(filename, context=self.context)
        if 'portal_factory' in self.context.getPhysicalPath():
            container = self.context.aq_parent.aq_parent.aq_parent
        else:
            container = self.context.aq_parent
        num = -1
        if self.context.getId()!=new_id:
            if not container.checkIdAvailable(new_id):
                base, ext = tuple(splitext(new_id))
                while (self.context.getId()!=new_id) and (not container.checkIdAvailable(new_id)):
                    num+=1
                    new_id = "%s-%02d%s" % (base, num, ext)
            #the savepoint is mandatory for portal_factory
            transaction.savepoint(optimistic=True)
            self.context.setId(new_id)
            #log.log("ID    : "+self.contextgetId()+" -> "+new_id)
            
        return new_id, num
    
