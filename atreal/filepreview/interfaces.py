# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import Datetime, TextLine, Object, Choice
from BTrees.Interfaces import IBTree
from datetime import datetime

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
    

class IPreviewConfiguration(Interface):
    """Configuration options
    """
    quality = Choice(
        title=_(u"arfilepreview_quality", default="Quality"),
        default=8,
        description=_(u"arfilepreview_quality_desc",
                      default=(u"Quality of the rendering")),
        values=range(1, 11)
        )


class IGlobalPreviewConfiguration(Interface):
    """Configuration options
    """

    quality = Choice(
        title=_(u"arfilepreview_quality", default="Quality"),
        default=8,
        description=_(u"arfilepreview_quality_desc",
                      default=(u"Quality of the rendering")),
        values=range(1, 11)
        )

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


class IPreviewable(Interface):

    html = TextLine(
        title=u"The html preview",
        default=u""
        )
    
    lastFileChange = Datetime(
        title=u"Date of the last change.",
        default=datetime.now()
        )
    
    lastPreviewUpdate = Datetime(
        title=u"Date of the last preview.",
        default=datetime.now()
        )
    
    subobjects = Object(
        title=u"Conversion datas.",
        schema=IBTree,
        )

