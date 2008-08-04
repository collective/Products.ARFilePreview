# -*- coding: utf-8 -*-

import re
import time
from DateTime import DateTime

from zope.interface import implements
from zope.component.interfaces import ComponentLookupError
from zope.component import queryUtility, adapts
from zope.traversing.adapters import Traverser
from zope.annotation.interfaces import IAnnotations

from plone.transforms.interfaces import ITransformEngine

from BTrees.OOBTree import OOBTree
from Products.Archetypes.utils import shasattr
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from Products.ARFilePreview.interfaces import *
from sd.common.fields.annotation import AdapterAnnotationProperty

_marker = object()

def chunk2gen(chunkedData):
    while not chunkedData is None:
        yield chunkedData.data
        chunkedData = chunkedData.next

def text2gen(Data):
    while len(Data):
        yield Data[:10000]
        Data = Data[10000:]

def chunk2ugen(chunkedData, charset):
    yield chunkedData.decode(charset, 'ignore')

def text2ugen(data, charset):
    while len(data):
        yield data[:10000].decode(charset)
        data = data[10000:]

def unicodegen(daddygen, charset):
    for data in daddygen:
        yield data.decode(charset)

class ToPreviewableObject( object ):

    adapts(IPreviewAware)
    implements(IPreviewable)

    html = AdapterAnnotationProperty(
        IPreviewable["html"],
        ns = "htmlpreview",
        )

    lastFileChange = AdapterAnnotationProperty(
        IPreviewable["lastFileChange"],
        ns = "htmlpreview",
        )

    lastPreviewUpdate = AdapterAnnotationProperty(
        IPreviewable["lastPreviewUpdate"],
        ns = "htmlpreview",
        )

    subobjects = AdapterAnnotationProperty(
        IPreviewable["subobjects"],
        ns = "htmlpreview",
        )
    
    _re_imgsrc = re.compile('<[iI][mM][gG]([^>]*) [sS][rR][cC]="([^">]*)"([^>]*)>')
    
    class _replacer(object):
        
        def __init__(self, sublist, instance):
            self.sublist = sublist
            self.instance = instance
        
        def __call__(self, match):
            prefix = match.group(1)
            inside = match.group(2)
            postfix = match.group(3)
            # patch inside
            if inside.startswith('./'):
                # some .swt are converted with this prefix
                inside = inside[2:]
            if inside in self.sublist:
                # convert elems that are known images 
                inside = '%s/@@preview_provider/%s' % (self.instance.getId(), inside)
            result = '<img%s src="%s"%s>' % (prefix, inside, postfix)
            return result
    

    def __init__(self, context):
        self.context = context
        if not self.subobjects:
            self.subobjects = OOBTree()

    def hasPreview(self):
        return bool(len(self.html))
    
    def setPreview(self, preview):
        self.html = preview
        #self.context.reindexObject()
    
    def getPreview(self, mimetype="text/html"):
        data = self.html
        if (mimetype!="text/html"
                and data is not None
                and data != ''):
            transforms = queryUtility(ITransformEngine)
            
            filename = self.context.getPrimaryField().getAccessor(self.context)().filename+".html"
            result = transforms.transform(data,'text/html', mimetype)
            if result is not None :
                return u''.join(result.data)
        return data

    def setSubObject(self, name, data):
        mtr = self.context.mimetypes_registry
        mime = mtr.classify(data, filename=name)
        mime = str(mime) or 'application/octet-stream'
        self.subobjects[name] = (data, mime)

    
    def getSubObject(self, id):
        if id in self.subobjects.keys():
            return self.subobjects[id]
        else:
            raise AttributeError
    
    def clearSubObjects(self):
        self.subobjects = OOBTree()
    
    def buildAndStorePreview(self):
        self.fileModified()
        result = self.prebuildPreview()
        self.reindexFilePreview()
        return result
        
    def prebuildPreview(self):
        print "Build and store preview"

        if getattr(self.context, 'isPreviewable', "always") == "never":
            return False
        transforms = queryUtility(ITransformEngine)

        field = self.context.getPrimaryField()
        fileobj = self.context.getFile()
        if not fileobj.data:
            print "No file data!"
            return False
        
        if self.context.isBinary(field.getName()):
            if shasattr(fileobj, 'getIterator'):
                data = fileobj.getIterator()
            elif isinstance(fileobj.data, (str, unicode)):
                data=text2gen(fileobj.data)
            else:
                data=chunk2gen(fileobj.data)
        else:
            if shasattr(fileobj, 'getIterator'):
                data = unicodegen(fileobj.getIterator())
            elif isinstance(fileobj.data, (str, unicode)):
                data = chunk2ugen(fileobj.data, 'utf-8')
            else:
                data = text2ugen(fileobj.data, 'utf-8')
        result = transforms.transform(data, field.getContentType(self.context),'text/html')

        if result is None:
            self.setPreview(u"")
            print "No preview!"
            return False
        
        #get the html code
        #XXX load all the html in memory.... We should have an iterator here, if possible
        html_converted = u''.join(result.data)
        #update internal links
        #remove bad character '\xef\x81\xac' from HTMLPreview
        html_converted = re.sub('\xef\x81\xac', "", html_converted)
        # patch image sources since html base is that of our parent
        subobjs = result.subobjects
        for subobj in subobjs.keys():
            # transorm iterators to strings for subobjects
            # we should return the iterator, but it's not possible in sub-objects right now...
            self.setSubObject(subobj, ''.join(subobjs[subobj]))
        html_converted = self._re_imgsrc.sub(self._replacer(subobjs.keys(), self.context), html_converted)
        
        #store the html in the HTMLPreview field for preview
        self.setPreview(html_converted)
        self.lastPreviewUpdate = time.time()
        return True
    
    def fileModified(self):
        """
        File has been modified ; store this date for further comparizon
        """
        self.clearSubObjects()
        self.html = u""
        self.lastFileChange = time.time()
    
    def updatePreview(self):
        """
        Update the preview
        """
        return self.buildAndStorePreview()
    
    def reindexFilePreview(self):
        return self.context.reindexObject(idxs=['SearchableText', 'lastPreviewUpdate','lastFileChange'])

_marker = object()

def previewIndexWrapper(object, portal, **kwargs):
    data = object.SearchableText()
    try:
        obj = IPreviewable(object)
        preview = obj.getPreview(mimetype="text/plain")
        return " ".join([data, preview])
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        return data

def lastPreviewUpdate(object, portal, **kwargs):
    if not IPreviewAware.providedBy(object):
        return
    obj=IAnnotations(object)
    preview_annot = obj.get('htmlpreview', _marker)
    if preview_annot is _marker:
        return DateTime(0)
    last_preview_update = preview_annot.get('lastPreviewUpdate', _marker)
    if last_preview_update is _marker:
        return DateTime(0)
    return last_preview_update

def lastFileChange(object, portal, **kwargs):
    if not IPreviewAware.providedBy(object):
        return
    obj=IAnnotations(object)
    preview_annot = obj.get('htmlpreview', _marker)
    if preview_annot is _marker:
        return DateTime(0)
    last_file_change = preview_annot.get('lastFileChange', _marker)
    if last_file_change is _marker:
        return DateTime(0)
    return last_file_change


registerIndexableAttribute('SearchableText', previewIndexWrapper)
registerIndexableAttribute('lastPreviewUpdate', lastPreviewUpdate)
registerIndexableAttribute('lastFileChange', lastFileChange)
