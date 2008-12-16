# -*- coding: utf-8 -*-

from five import grok
from Acquisition import aq_base
from interfaces import IPreviewable, IPreviewAware
from zope.lifecycleevent import ObjectModifiedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
import logging


@grok.subscribe(IPreviewAware, ObjectModifiedEvent)
@grok.subscribe(IPreviewAware, IObjectInitializedEvent)
def buildAndStorePreview(obj, event):
    u"""
    We get a buildAndStorePreview request.
    Let's check wether we have to do it or not, depending on options
    and test wether file has been modified or not.
    If this is ok, call the adapter's method buildAndStorePreview.
    """   
    logger = logging.getLogger('buildAndStorePreview')
    #print "BUILD AND STORE PREVIEW %s on %s" % (obj.getPhysicalPath(),event)
    form = obj.REQUEST.form
    if form.get('file_delete', 'changed') == "nochange":
        msg = ("File field of %s has not changed"
              ": no preview computation" % "/".join(obj.getPhysicalPath()))
        logger.log(logging.INFO, msg)
        # file is modified ; dirty preview
        previewable.fileModified()
        previewable.reindexFilePreview()
        return
    
    previewable = IPreviewable(obj)
    isPreviewable = getattr(obj, 'isPreviewable', "always")
    if isPreviewable == "always":
        previewable.buildAndStorePreview()
    else:
        # file is modified ; dirty preview
        previewable.fileModified()
        previewable.reindexFilePreview()
        msg = ("File's preview option is %s"
              ": no new preview for %s " % (isPreviewable,
                                            "/".join(obj.getPhysicalPath())))
