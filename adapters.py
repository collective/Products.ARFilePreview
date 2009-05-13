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
from DateTime import DateTime

from zope.interface import implements
from zope.component.exceptions import ComponentLookupError
from zope.app.traversing.adapters import Traverser
from zope.app.annotation.interfaces import IAnnotations

from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName
from Products.ARFilePreview.interfaces import IPreviewable
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

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
    
    def hasPreview(self):
        return bool(len(self.annotations[self.key]['html']))
    
    def setPreview(self, preview):
        self.annotations[self.key]['html'] = preview
        self.context.reindexObject()
    
    def getPreview(self, mimetype="text/html"):
        data = self.annotations[self.key]['html']
        if mimetype!="text/html" and data is not None and data != '' :
            transforms = getToolByName(self.context, 'portal_transforms')
            filename = self.context.getPrimaryField().getAccessor(self.context)().filename+".html"
            return str(transforms.convertTo(mimetype, data.encode('utf-8'), mimetype="text/html", filename = filename)).decode('utf-8')
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
        self.clearSubObjects()
        transforms = getToolByName(self.context, 'portal_transforms')
        file = self.context.getPrimaryField().getAccessor(self.context)()
        data = transforms.convertTo('text/html', self.context.get_data(), filename=file.filename)
        
        if data is None:
            self.setPreview(u"")
            return
        
        #get the html code
        html_converted = data.getData()
        #update internal links
        #remove bad character '\xef\x81\xac' from HTMLPreview
        html_converted = re.sub('\xef\x81\xac', "", html_converted)
        # patch image sources since html base is that of our parent
        subobjs = data.getSubObjects()
        if len(subobjs)>0:
            for id, data in subobjs.items():
                self.setSubObject(id, data)
            html_converted = self._re_imgsrc.sub(self._replacer(subobjs.keys(), self.context), html_converted)
        #store the html in the HTMLPreview field for preview
        self.setPreview(html_converted.decode('utf-8', "replace"))
        self.context.reindexObject()

def previewIndexWrapper(object, portal, **kwargs):
    data = object.SearchableText()
    try:
        obj = IPreviewable(object)
        preview = obj.getPreview(mimetype="text/plain")
        return " ".join([data, preview.encode('utf-8')])
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        return data

#registerIndexableAttribute('SearchableText', previewIndexWrapper)


