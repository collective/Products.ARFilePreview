#-*- coding: utf-8 -*-

from Products.ATContentTypes.content.file import ATFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from SubMapper import SubMapper
from schemas import SpeedFileSchema
from interfaces import ISpeedFile
from zope.interface import implements


class SpeedFile(ATFile):

    implements(ISpeedFile)
    schema = ATFile.schema.copy() + SpeedFileSchema

    
    def updateMetadata(self):
       """
       This method calls the metadata extractor from meta.py
       """
       setmetas(self)
        
    def updateTitleFromMetas(self, newTitle=None, num=-1):
        """
        This method sets the title from the metadata
        """
        if len(self.getSujet())>0:
            newTitle=self.getSujet()
        elif (self.description!=None) and (len(self.description)>0):
            newTitle=self.Description
        else:
            if newTitle is None:
                newTitle=self.getOriginalFile().filename
            if num>=0:
                base, ext = splitext(newTitle)
                newTitle="%s-%02d%s"%(base, num, ext)
            newTitle = re.sub("[_-]"," ", newTitle)
        
        if newTitle!=self.Title:
            self.update(title=newTitle)
    
    
    def updateAydi(self, filename):
        """
        This method sets the id from the filename
        """
        #log = LogClass(self, "updateAydi", indent=1)
        plone_utils = getToolByName(self, 'plone_utils', None)
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
            #log.log("ID    : "+self.getId()+" -> "+new_id)
        return new_id, num
    
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
                if 'OriginalFile_file' in REQUEST.keys():
                    splat=splitext(REQUEST['OriginalFile_file'].filename)
                    REQUEST['OriginalFile_file'].filename=splat[0]+splat[1].lower()
    
