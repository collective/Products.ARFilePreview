# -*- coding: utf-8 -*-

import re
import time
import troll.storage as storage
from five import grok
from atreal.filepreview.storage import BlobFileInformation
from zope.component import queryUtility, createObject
from zope.annotation.interfaces import IAnnotations
from plone.transforms.interfaces import ITransformEngine
from Products.Archetypes.utils import shasattr
from utils import chunk2gen, text2gen, chunk2ugen, text2ugen, unicodegen
from interfaces import *
from htmlentitydefs import codepoint2name

_re_imgsrc = re.compile('<[iI][mM][gG]([^>]*) [sS][rR][cC]="([^">]*)"([^>]*)>')


def htmlentities(u):
    result = []
    for c in u:
        if ord(c) < 128 or c == ' ':
            result.append(c)
        else:
            result.append('&%s;' % codepoint2name.get(ord(c), 'nbsp'))
    return ''.join(result)


class ToPreviewableObject(storage.BaseStorageHandler):
    grok.context(IPreviewAware)
    grok.provides(IPreviewable)

    info = storage.AnnotationContainerProperty(
        IPreviewable['info'],
        ns='atreal.filepreview.info'
        )

    storage = storage.AnnotationContainerProperty(
        IPreviewable['storage'],
        ns='atreal.filepreview.previews'
        )

    def __init__(self, context):
        storage.BaseStorageHandler.__init__(self, context)
        if not hasattr(self.storage, 'lastPreviewUpdate'):
            self.storage.lastPreviewUpdate = None
        if not hasattr(self.storage, 'lastFileChange'):
            self.storage.lastFileChange = None
        
    def clear(self):
        self.storage = storage.container.GenericStorage()
        
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
        creator = IPreviewCreator(self.context)
        preview = creator.create(u'html', preview)
        print 'Storing preview as %r' % preview
        self.store(preview)
        
    
    def getPreview(self, mimetype="text/html"):
        html = self.retrieve(u'html')
        data = html is not None and html.data or None
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
        obj = IPreviewCreator(self.context).create(name, data)
        return self.store(obj)

    def getSubObject(self, id):
        return self.retrieve(id)
    
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
            self.delete(u'html')
            print "No preview!"
            return False
        
        #get the html code
        #XXX load all the html in memory.... We should have an iterator here, if possible
        html_converted = u''.join(result.data)
        #update internal links
        #remove bad characters
        html_converted = re.sub('\xef\x81\xac', "", html_converted)
        # patch image sources since html base is that of our parent
        subobjs = result.subobjects
        for subobj in subobjs.keys():
            # transorm iterators to strings for subobjects
            # we should return the iterator, but it's not possible in sub-objects right now...
            self.setSubObject(subobj, ''.join(subobjs[subobj]))
        html_converted = _re_imgsrc.sub(
            self._replacer(subobjs.keys(), self.context), html_converted
            )
        
        #store the html in the HTMLPreview field for preview
        self.setPreview(htmlentities(html_converted))
        self.storage.lastPreviewUpdate = time.time()
        return True
    
    def fileModified(self):
        """
        File has been modified ; store this date for further comparizon
        """
        self.clear()
        self.storage.lastFileChange = time.time()
    
    def updatePreview(self):
        """
        Update the preview
        """
        return self.buildAndStorePreview()
    
    def reindexFilePreview(self):
        return self.context.reindexObject(
            idxs=['SearchableText', 'lastPreviewUpdate','lastFileChange']
            )
