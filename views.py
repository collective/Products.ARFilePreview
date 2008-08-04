# -*- coding: utf-8 -*-
#
# File: ARFilePreview/views.py
#
# Copyright (c) 2007 atReal
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
$Id$
"""

__author__ = """Jean-Nicolas Bès <contact@atreal.net>"""
__docformat__ = 'plaintext'
__licence__ = 'GPL'

# Imports: Zope
from Acquisition import aq_inner
from Products.Five  import BrowserView
from zope.event import notify
from zope.interface import implements

# Imports: CMF
from Products.CMFCore.utils import getToolByName

# Import Plone
from Products.CMFPlone import MessageFactory
mf = MessageFactory('eventsubscription')

# Imports: Archetypes
from Products.Archetypes.BaseObject import Wrapper

# Imports: ARFilePreview
from Products.ARFilePreview.interfaces import IPreviewable
from Products.ARFilePreview.interfaces import IPreviewProvider

import transaction
import logging

class PreviewProvider( BrowserView ):

    implements( IPreviewProvider )
  
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.object = IPreviewable(context)
       
    def hasPreview(self):
        u"""
        """
        return self.object.hasPreview()
  
    def getPreview(self):
        u"""
        """
        return self.object.getPreview() 
    
    def updatePreview(self):
        u"""
        """
        self.object.buildAndStorePreview()

    def updatePreviewOnDemand(self):
        u"""
        """
        self.object.buildAndStorePreview()
        self.request.response.redirect(self.context.absolute_url()+'/view')


    ## XXX This should NOT be here !!
    ## but I wanted the feature badly...
    def updateAllPreviews(self, updateNewOnly = False):
        u"""
        update all objects' preview ; may be usefull if you change a transform
        """
        logger = logging.getLogger('UpdateAllPreviewsLog')
        pc = self.context.portal_catalog
        #brains = pc(portal_type='File')
        brains = pc(
            object_provides="Products.ARFilePreview.interfaces.IPreviewAware",
            sort_on='modified',
            sort_order='reverse')
        
        status=""
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
        msg = "updateAllPreviews : done"
        if updateNewOnly:
            msg += " (only files newly updated)"
        status+= "<div>%s </div>" % msg
        logger.log(logging.INFO, msg)
        return status
    
    def updateNewPreviews(self):
        u"""
        update all modified objects' preview
        can be run in a periodic batch
        """
        status = self.updateAllPreviews(updateNewOnly = True)
        return status

    def __bobo_traverse__(self, REQUEST, name):
        u'''transparent access to document subobjects
        '''
        try:
            data, mime = self.object.getSubObject(name)
        except AttributeError:
            pass
        else:
            return Wrapper(data, name, mime).__of__(self)
        return getattr(self, name)

