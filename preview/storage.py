# -*- coding: utf-8 -*-

from zope.component import adapts
from sd.common.fields.annotation import AdapterAnnotationProperty
from sd.common.adapters.storage.annotation import GenericAnnotationStorage
from sd.common.adapters.storage.interfaces import IStorage, IStorageItem
from sd.common.adapters.storage.interfaces import IDictStorage
from Products.ARFilePreview.interfaces import IPreviewAware


class PreviewInformation(SimpleItem):
    implements(IStorageItem)
    name = FieldProperty(IStorageItem['name'])
    data = Attribute("The data to store")
    mime = Attribute("Mimetype of the file")

    def __init__(self, name, data, mime):
        self.name = name
        self.data = data
        self.mime = mime


class PreviewInformationStorage(GenericAnnotationStorage):
    """Provides a storage for preview information. The storage is a dictionnary
    and everything is persisted in an annotation.
    """
    adapts(IStructuredItem)
    
    storage = AdapterAnnotationProperty(
        IDictStorage['storage'],
        ns="arfilepreview.subobjects"
        )
