# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import Datetime, TextLine, Object
from BTrees.Interfaces import IBTree
from datetime import datetime


class IPreviewAware(Interface):
    """Marker interface
    """


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
    
