# -*- coding: utf-8 -*-
#
# File: ARFilePreview/adapters.py
#
# Copyright (c) 2007 atReal
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
$Id$
"""

__author__ = """Jean-Nicolas Bès <contact@atreal.net>"""
__docformat__ = 'plaintext'
__licence__ = 'GPL'

import re
import time
from DateTime import DateTime

from zope.interface import implements
from zope.component.interfaces import ComponentLookupError
from zope.component import queryUtility
from zope.traversing.adapters import Traverser
from zope.annotation.interfaces import IAnnotations

from plone.transforms.interfaces import ITransformEngine

from BTrees.OOBTree import OOBTree
from Products.Archetypes.utils import shasattr
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from Products.ARFilePreview.interfaces import IPreviewable

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
    
    implements( IPreviewable )
    
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
        self.key         = 'htmlpreview'
        self.context     = context
        self.annotations = IAnnotations(context)
        if not self.annotations.get(self.key, None):
            self.annotations[self.key] = OOBTree()
        if not self.annotations[self.key].get('html', None):
            self.annotations[self.key]['html'] = ""
        if not self.annotations[self.key].get('subobjects', None):
            self.annotations[self.key]['subobjects'] = OOBTree()
        if not self.annotations[self.key].get('lastFileChange', None):
            self.annotations[self.key]['lastFileChange'] = 0
        if not self.annotations[self.key].get('lastPreviewUpdate', None):
            self.annotations[self.key]['lastPreviewUpdate'] = 0
    
    def hasPreview(self):
        return bool(len(self.annotations[self.key]['html']))
    
    def setPreview(self, preview):
        self.annotations[self.key]['html'] = preview
        self.context.reindexObject()
    
    def getPreview(self, mimetype="text/html"):
        data = self.annotations[self.key]['html']
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
        self.annotations[self.key]['subobjects'][name] = (data, mime)
    
    def getSubObject(self, id):
        if id in self.annotations[self.key]['subobjects'].keys():
            return self.annotations[self.key]['subobjects'][id]
        else:
            raise AttributeError
    
    def clearSubObjects(self):
        self.annotations[self.key]['subobjects'] = OOBTree()
    
    def buildAndStorePreview(self):
        print "Build and store preview"
        if getattr(self.context, 'isPreviewable', "always") == "never":
            self.clearSubObjects()
            self.setPreview(u'')
            return False
        self.clearSubObjects()
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
        self.annotations[self.key]['lastPreviewUpdate'] = time.time()
        self.context.reindexObject()
        return True
    
    def fileModified(self):
        """
        File has been modified ; store this date for further comparizon
        """
        self.annotations[self.key]['lastFileChange'] = time.time()
    
    def updatePreview(self):
        """
        Update the preview
        """
        return self.buildAndStorePreview()

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
    obj=IPreviewable(object)
    return obj.annotations[obj.key]['lastPreviewUpdate']

def lastFileChange(object, portal, **kwargs):
    obj=IPreviewable(object)
    return obj.annotations[obj.key]['lastFileChange']

registerIndexableAttribute('SearchableText', previewIndexWrapper)
registerIndexableAttribute('lastPreviewUpdate', lastPreviewUpdate)
registerIndexableAttribute('lastFileChange', lastFileChange)
