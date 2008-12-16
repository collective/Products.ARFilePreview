# -*- coding: utf-8 -*-

# Imports: Zope
from five import grok
from zope.cachedescriptors.property import CachedProperty
from Products.Archetypes.BaseObject import Wrapper
from atreal.filepreview import interfaces
from plone.app.layout.viewlets.interfaces import IBelowContentBody

grok.templatedir('templates')


class Fullview(grok.View):

    grok.name('preview')
    grok.require('zope2.View')
    grok.context(interfaces.IPreviewAware)
    grok.implements(interfaces.IPreviewProvider)

    @CachedProperty
    def object(self):
        return interfaces.IPreviewable(self.context)
       
    def hasPreview(self):
        return self.object.hasPreview()
  
    def getPreview(self):
        return self.object.getPreview() 
    
    def updatePreview(self):
        self.object.buildAndStorePreview()

    def updatePreviewOnDemand(self):
        self.object.buildAndStorePreview()
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def publishTraverse(self, request, name):
        info = self.object.getSubObject(name)
        if info is not None:
            return Wrapper(info.data, info.name, info.mime).__of__(self)
        return getattr(self, name)


class FileAsDoc(grok.View):
    grok.name('file_asdoc')
    grok.require('zope2.View')
    grok.context(interfaces.IPreviewAware)


class FilePreview(grok.View):
    grok.name('file_preview')
    grok.require('zope2.View')
    grok.context(interfaces.IPreviewAware)


class PreviewConfiguration(grok.Viewlet):
    grok.name('atreal.filepreview.localconfigure')
    grok.require('cmf.ModifyPortalContent')
    grok.viewletmanager(IBelowContentBody)
    grok.context(interfaces.IPreviewAware)
