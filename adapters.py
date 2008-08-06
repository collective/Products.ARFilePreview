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
from Products.ARFilePreview.interfaces import IPreviewAware

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
        char = ord(data[-1])
        if charset == 'utf-8' and char>127:
            if not(char & 32):
                num = 1
            elif not(char & 16):
                num = 2
            elif not(char & 8):
                num = 3
            else:
                print char
                raise "Invalid utf-8 boundary"
            nextblock = daddygen.next()
            yield (data + nextblock[0:num]).decode(charset)
            yield (nextblock[num:]).decode(charset)
        else:
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
        #self.context.reindexObject()
    
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
        self.fileModified()
        result = self.prebuildPreview()
        self.reindexFilePreview()
        return result
        
    def getDataAndContenttype(self):
        field = self.context.getPrimaryField()
        fileobj = self.context.getFile()
        if not fileobj.data:
            print "No file data!"
            return False
        try:
            isbinary = self.context.isBinary(field.getName())
        except AssertionError:
            # object not binary ; maybe blobfile
            isbinary = False
        
        if isbinary:
            if shasattr(fileobj, 'getIterator'):
                data = fileobj.getIterator()
            elif isinstance(fileobj.data, (str, unicode)):
                data=text2gen(fileobj.data)
            else:
                data=chunk2gen(fileobj.data)
        else:
            if shasattr(fileobj, 'getIterator'):
                data = unicodegen(fileobj.getIterator(), 'utf-8')
            elif isinstance(fileobj.data, (str, unicode)):
                data = chunk2ugen(fileobj.data, 'utf-8')
            else:
                data = text2ugen(fileobj.data, 'utf-8')
        return ( data, field.getContentType(self.context) )
        
        
    def prebuildPreview(self):
        if getattr(self.context, 'isPreviewable', "always") == "never":
            return False

        data, contenttype = self.getDataAndContenttype()
        transforms = queryUtility(ITransformEngine)
        result = transforms.transform(data, contenttype,'text/html')

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
        return True
    
    def fileModified(self):
        """
        File has been modified ; store this date for further comparizon
        """
        self.clearSubObjects()
        self.setPreview(u'')
        self.annotations[self.key]['lastFileChange'] = time.time()
    
    def updatePreview(self):
        """
        Update the preview
        """
        return self.buildAndStorePreview()
    
    def reindexFilePreview(self):
        return self.context.reindexObject(idxs=['SearchableText', 'lastPreviewUpdate','lastFileChange'])

_marker = object()

def previewIndexWrapper(object, portal, **kwargs):
    direct_files_index_list = ["application/vnd.ms-excel", "application/msexcel", "application/pdf",]
    data = object.SearchableText()
    if not isinstance(data, unicode):
        data = data.decode('utf-8', 'ignore')
    try:
        obj = IPreviewable(object)
        objectdata, contenttype = obj.getDataAndContenttype()
        if contenttype in direct_files_index_list :
            transforms = queryUtility(ITransformEngine)
            preview = transforms.transform(objectdata, contenttype, 'text/plain').data
            preview = "".join(preview)
        else:
            preview = obj.getPreview(mimetype="text/plain")
        return u" ".join([data, preview])
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
