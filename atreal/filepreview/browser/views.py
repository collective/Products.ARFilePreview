# -*- coding: utf-8 -*-

# Imports: Zope
from five import grok
from zope.cachedescriptors.property import CachedProperty
from Products.Archetypes.BaseObject import Wrapper
from atreal.filepreview import interfaces
from plone.app.layout.viewlets.interfaces import IBelowContentBody
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import ITraversable
from sd.common.adapters.storage.interfaces import IDictStorage
from zope.publisher.interfaces import NotFound
        
grok.templatedir('templates')


class PreviewUpdater(grok.View):
    grok.name('preview_updater')
    grok.require('cmf.ModifyPortalContent')
    grok.context(interfaces.IPreviewAware)

    @property
    def previewable(self):
        return interfaces.IPreviewable(self.context)
           
    def updatePreview(self):
        self.previewable.buildAndStorePreview()

    def updatePreviewOnDemand(self):
        self.previewable.buildAndStorePreview()
        self.request.response.redirect(self.context.absolute_url()+'/view')

    def publishTraverse(self, request, name):
        if name in ['updatePreview', 'updatePreviewOnDemand']:
            return getattr(self, name)()
        return self.render()

    def render(self):
        return u""


class FileAsDoc(grok.View):
    grok.name('file_as_doc')
    grok.require('zope2.View')
    grok.context(interfaces.IPreviewAware)

    def getPreview(self):
        previewable = interfaces.IPreviewable(self.context)
        return previewable.getPreview() 


class FullscreenPreview(FileAsDoc):
    grok.name('fullscreen_preview')
    grok.template('previewdisplay')


class PreviewDisplay(grok.Viewlet):
    grok.name('atreal.filepreview.display')
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentBody)
    grok.context(interfaces.IPreviewAware)

    @property
    def hide(self):
        return self.view.__name__ == u'file_as_doc'

    def getPreview(self):
        previewable = interfaces.IPreviewable(self.context)
        return previewable.getPreview() 


class PreviewTraverser(grok.MultiAdapter):
    grok.name("preview")
    grok.adapts(interfaces.IPreviewAware, IHTTPRequest)
    grok.provides(ITraversable)
	   
    def __init__(self, context, request=None):
        self.context = context
        self.request = request       

    def traverse(self, name, ignore):
        info = IDictStorage(self.context).retrieve(name)
        if info is None:
            raise NotFound(self.context, name, self.request)
    
        return Wrapper(info.data, info.name, info.mime).__of__(self.context)
