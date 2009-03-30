# -*- coding: utf-8 -*-

import troll.storage as storage
from datetime import datetime
from zope.interface import Interface
from zope.schema import Datetime, TextLine, Object, Choice


from zope.i18nmessageid import MessageFactory
_ = MessageFactory("arfilepreview")


class IPreviewAware(Interface):
    """Marker interface
    """

class IGlobalPreviewHandler(Interface):
    """
    """

class IPreviewCreator(Interface):

    def create(self, name, data):
        """Returns a storage item.
        """
    
class IGlobalPreviewConfiguration(Interface):
    """Configuration options
    """
    preview_display = Choice(
        title=_(u"arfilepreview_display", default="Display of the preview"),
        default="Embedded",
        description=_(u"arfilepreview_display_desc",
                      default=(u"How should the preview be "
                               u"displayed on the file view")),
        values=[u"Embedded",
                u"Popup",
                u"Disabled",
                u"iFrame"]
        )


class IPreviewable(storage.IStorageHandler):
    """Contains information about the transformation
    """
    info = Object(
        title = u"Generic information containment",
        description = u"Transformation info.",
        schema = storage.IStorage,
        required = True,
        readonly = False
        )
    
    def getPreview(mime):
        """Returns the preview in the demanded mimetype.
        """
