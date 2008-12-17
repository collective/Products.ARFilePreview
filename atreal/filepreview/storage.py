# -*- coding: utf-8 -*-

import os
from five import grok
from OFS.SimpleItem import SimpleItem
from Products.blob.file import FileBlob
from zope.interface import implements, Attribute
from zope.schema.fieldproperty import FieldProperty
from sd.common.fields.annotation import AdapterAnnotationProperty
from sd.common.adapters.storage.annotation import GenericAnnotationStorage
from sd.common.adapters.storage.interfaces import IStorageItem, IDictStorage
from atreal.filepreview.interfaces import IPreviewAware, IPreviewCreator
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.file import IATFile
from Products.BlobFile.file import BlobFile


class SimpleFileInformation(SimpleItem):
    implements(IStorageItem)
    name = FieldProperty(IStorageItem['name'])
    data = Attribute("The data to store")
    mime = Attribute("Mimetype of the file")

    def __init__(self, name, data, mime):
        self.name = unicode(name)
        self.data = data
        self.mime = mime


class BlobFileInformation(SimpleFileInformation):

    path = Attribute("Filesystem location of the data.")
    _blob = None

    def __init__(self, name, data, mime, path):
        self.name = unicode(name)
        self.mime = mime
        self.path = path
        self.data = data

    def setData(self, value):
        os.environ['BLOB_DIR'] = self.path
        blob = self._blob = FileBlob()
        file = blob.open('wb')
        file.write(value)
        file.close()
        return blob

    def getData(self):
        os.environ['BLOB_DIR'] = self.path
        file = self._blob.open('r')
        data = file.read()
        file.close()
        return data

    data = property(getData, setData)
    

class PreviewInformationStorage(GenericAnnotationStorage):
    grok.context(IPreviewAware)
    storage = AdapterAnnotationProperty(
        IDictStorage['storage'],
        ns="atreal.filepreview"
        )

    def clear(self):
        self.storage = dict()


class BasePreviewCreator(grok.Adapter):
    grok.baseclass()

    def guess_mime(self, name, data):
        mtr = self.context.mimetypes_registry
        mime = mtr.classify(data, filename=name)
        return str(mime) or 'application/octet-stream'
    

class SimplePreviewCreator(BasePreviewCreator):
    grok.context(IATFile)
    grok.implements(IPreviewCreator)
 
    def create(self, name, data):
        mime = self.guess_mime(name, data)
        return SimpleFileInformation(name, data, mime)


class BlobPreviewCreator(BasePreviewCreator):
    grok.context(BlobFile)
    grok.implements(IPreviewCreator)

    def create(self, name, data):
        btool = getToolByName(self.context, 'portal_blob')
        mime = self.guess_mime(name, data)
        path = btool.getBlobDir()
        return BlobFileInformation(name, data, mime, path)
