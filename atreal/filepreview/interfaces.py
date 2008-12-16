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

    #### THIS IS JUST FOR THE DEMO
    quality = Choice(
        title=_(u"arfilepreview_quality", default="Quality"),
        default=8,
        description=_(u"arfilepreview_quality_desc",
                      default=(u"Quality of the rendering")),
        values=range(1, 11)
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

   
class IPreviewProvider( Interface ):
    
    def hasPreview( ):
        """
        Has the preview
        """
    
    def getPreview( ):
        """
        Get the preview
        """
        
    def updatePreview( ):
        """
        update the preview by retransforming original file and store it
        """
    
    def updatePreviewOnDemand( ):
        """
        update the preview by retransforming original file and store it,
        the redirect to the object.
        """
    
    def updateAllPreviews( ):
        """
        update all the previews reachable from the catalog
        """
    
    def updateNewPreviews( ):
        """
        update the previews reachable from the catalog, for new files only
        """
