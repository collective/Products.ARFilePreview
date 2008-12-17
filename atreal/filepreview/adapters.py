# -*- coding: utf-8 -*-

import re
import time
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from zope.component import queryUtility, adapts
from zope.interface import implements, Attribute
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAnnotations
from plone.transforms.interfaces import ITransformEngine
from Products.Archetypes.utils import shasattr

from sd.common.fields.annotation import AdapterAnnotationProperty
from sd.common.adapters.storage.interfaces import IDictStorage, IStorageItem
from sd.common.adapters.storage.annotation import GenericAnnotationStorage

from interfaces import IPreviewAware, IPreviewConfiguration, IPreviewable

from five import grok
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



class PreviewInformation(SimpleItem):
    implements(IStorageItem)
    name = FieldProperty(IStorageItem['name'])
    data = Attribute("The data to store")
    mime = Attribute("Mimetype of the file")

    def __init__(self, name, data, mime):
        self.name = unicode(name)
        self.data = data
        self.mime = mime

class PreviewStorage(GenericAnnotationStorage):
    grok.context(IPreviewAware)
    storage = AdapterAnnotationProperty(
        IDictStorage['storage'],
        ns="atreal.filepreview"
        )

    def clear(self):
        self.storage = dict()

class PreviewConfigurationAdapter(grok.Adapter):
    """This adapter will not yield to kiss the ground before your feet.
    Instead, it will write the fields' values in an annotation :)
    """
    grok.context(IPreviewAware)
    implements(IPreviewConfiguration)
    
    # Annotation fields
    quality = AdapterAnnotationProperty(
        IPreviewConfiguration["quality"],
        ns = "atreal.filepreview.configuration",
        )

class ToPreviewableObject(grok.Adapter):

    grok.context(IPreviewAware)
    implements(IPreviewable)

    html = AdapterAnnotationProperty(
        IPreviewable["html"],
        ns = "atreal.filepreview.info",
        )

    lastFileChange = AdapterAnnotationProperty(
        IPreviewable["lastFileChange"],
        ns = "atreal.filepreview.info",
        )

    lastPreviewUpdate = AdapterAnnotationProperty(
        IPreviewable["lastPreviewUpdate"],
        ns = "atreal.filepreview.info",
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
                inside = '%s/++preview++%s' % (self.instance.getId(), inside)
            result = '<img%s src="%s"%s>' % (prefix, inside, postfix)
            return result
    

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
        subobj = PreviewInformation(name, data, mime)
        return IDictStorage(self.context).store(subobj)

    def getSubObject(self, id):
        return IDictStorage(self.context).retrieve(id)

    def clearSubObjects(self):
        return IDictStorage(self.context).clear()
    
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
        result = transforms.transform(data,
                                      field.getContentType(self.context),
                                      'text/html')

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
        html_converted = self._re_imgsrc.sub(
            self._replacer(subobjs.keys(), self.context), html_converted
            )
        
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
        return self.context.reindexObject(
            idxs=['SearchableText', 'lastPreviewUpdate','lastFileChange']
            )
