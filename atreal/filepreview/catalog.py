# -*- coding: utf-8 -*-

from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from interfaces import IPreviewable


def previewIndexWrapper(object, portal, **kwargs):
    data = unicode(object.SearchableText(), "utf-8")
    obj = IPreviewable(object, None)
    if obj is not None:
        preview = obj.getPreview(mimetype="text/plain")
        return " ".join([data, preview])
    return data

def lastPreviewUpdate(object, portal, **kwargs):    
    obj = IPreviewable(object, None)
    return obj and obj.lastPreviewUpdate or None

def lastFileChange(object, portal, **kwargs):
    obj = IPreviewable(object, None)
    return obj and obj.lastFileChange or None


registerIndexableAttribute('SearchableText', previewIndexWrapper)
registerIndexableAttribute('lastPreviewUpdate', lastPreviewUpdate)
registerIndexableAttribute('lastFileChange', lastFileChange)
