# -*- coding: utf-8 -*-

import logging
import transaction

from five import grok
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from zope.component import getUtility
from zope.schema.fieldproperty import FieldProperty
from Products.CMFPlone.Portal import PloneSite
from interfaces import IGlobalPreviewConfiguration, IGlobalPreviewHandler, IPreviewable


@grok.adapter(PloneSite)
@grok.implementer(IGlobalPreviewConfiguration)
def arfilepreview_global_configuration(context):
    """Adapting plone site to furnish the wanted utility
    """
    return getUtility(IGlobalPreviewConfiguration,
                      name='arfilepreview.configuration',
                      context=context)


class GlobalConfiguration(SimpleItem):
    implements(IGlobalPreviewConfiguration)
    preview_display = FieldProperty(IGlobalPreviewConfiguration['preview_display'])


class GlobalPreviewHandler(grok.GlobalUtility):
    grok.implements(IGlobalPreviewHandler)

    def updateAllPreviews(self, context, updateNewOnly = False):
        u"""
        update all objects' preview ; may be usefull if you change a transform
        """
        logger = logging.getLogger('UpdateAllPreviewsLog')
        pc = context.portal_catalog
        #brains = pc(portal_type='File')
        brains = pc(
            object_provides="atreal.filepreview.interfaces.IPreviewAware",            
            sort_on='modified',
            sort_order='reverse')
        
        status=""
        error = 0
        for brain in brains:
            if updateNewOnly and ( brain.lastFileChange < brain.lastPreviewUpdate ):
                continue
            status+="<div>"+brain.getPath()
            logger.log(logging.INFO, brain.getPath())
            try:
                obj=brain.getObject()
                IPreviewable(obj).updatePreview()
                obj.reindexObject()
                
            except Exception, e:
                msg = "%s %s %s" % (brain.getPath(), str(e.__class__.__name__), str(e))
                status+= "%s </div>" % msg
                logger.log(logging.ERROR, msg)
                error += 1
            else:
                msg = "%s OK" % (brain.getPath(),)
                status+= "%s </div>" % msg
                logger.log(logging.INFO, msg)
            try:
                transaction.commit()
            except Exception, e:
                msg = "Commit error on object %s : %s %s ; trying abort" % (brain.getPath(), str(e.__class__.__name__), str(e))
                logger.log(logging.ERROR, msg)
                try:
                    transaction.abort()
                except:
                    msg = "Abort error on object %s : %s %s " % (brain.getPath(), str(e.__class__.__name__), str(e))
                    logger.log(logging.ERROR, msg)
                    pass
        if not status:
            msg = "updateAllPreviews : No preview have been updated"
        else:
            msg = "updateAllPreviews : done"
            if updateNewOnly:
                msg += " (only files newly updated)"
        status+= "<div>%s </div>" % msg
        logger.log(logging.INFO, msg)
        return error, status
    
    def updateNewPreviews(self, context):
        u"""
        update all modified objects' preview
        can be run in a periodic batch
        """
        error, status = self.updateAllPreviews(context, updateNewOnly = True)
        return error, status
