from Products.ARFilePreview.interfaces import *
from sd.common.fields.annotation import AdapterAnnotationProperty
from sd.common.adapters.base import BaseAdapter
from sd.common.adapters.storage.interfaces import IStorage
from storage import PreviewInformationStorage, PreviewInformation


class PreviewInformationProvider(BaseAdapter):
    """Adapter provider the basic attributes of a file preview
    """
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


class PreviewProvider(PreviewInformationProvider):

    def store_information(self, name, data):
        storage = IStorage(self.context)
        mtr = self.context.mimetypes_registry
        mime = mtr.classify(data, filename=name)
        mime = str(mime) or 'application/octet-stream'
        info = PreviewInformation(name, data, mime)
        storage.store
