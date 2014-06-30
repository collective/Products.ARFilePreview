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
from zope.component import queryUtility
from zope.component import getMultiAdapter

# Imports: CMF
from Products.CMFCore.utils import getToolByName

# Import Plone
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from Products.CMFPlone import MessageFactory
mf = MessageFactory('eventsubscription')

# Imports: ARDeadline
from Products.ARFilePreview.interfaces import IPreviewable
from Products.ARFilePreview.interfaces import IPreviewProvider
from Products.Archetypes.BaseObject import Wrapper
from events import buildAndStorePreview

try:
    from eea.annotator.portlets.annotator import Assignment
except ImportError:
    Assignment = None

try:
    from plonetheme.drincorda.patches import my_enable
except ImportError:
    my_enable = None

class GenPreview(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def add_portlet(self, target):
        if not Assignment:
            return
        manager = queryUtility(IPortletManager, 'plone.rightcolumn',
            context=target)
        assignments = getMultiAdapter((target, manager),
            IPortletAssignmentMapping)
        if 'inline-comments' not in assignments:
            assignments['inline-comments'] = Assignment()

    def __call__(self):
        target = self.context
        buildAndStorePreview(target, None)
        target.setLayout('file_asdoc')
        self.add_portlet(target)
        if my_enable:
            my_enable(target)
        self.request.response.redirect(target.absolute_url() + '/view')

class PreviewProvider( BrowserView ):

    implements( IPreviewProvider )
  
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.object = IPreviewable(context)
       
    def hasPreview(self):
        """
        """
        return self.object.hasPreview()
  
    def getPreview(self):
        """
        """
        return self.object.getPreview()
    
    def updatePreview(self):
        """
        """
        self.object.buildAndStorePreview()
    

    ## XXX This should NOT be here !!
    ## but I wanted the feature badly...
    def updateAllPreviews(self):
        """
        """
        pc = self.context.portal_catalog
        brains = pc(portal_type='File')
        status=""
        for brain in brains:
            status+="<div>"+brain.getPath()
            try:
                obj=brain.getObject()
                IPreviewable(obj).buildAndStorePreview()
                obj.reindexObject()
            except Exception, e:
                status+=" %s %s</div>" % (str(e.__class__.__name__), str(e))
            else:
                status+=" OK</div>\n"
        return status


    def __bobo_traverse__(self, REQUEST, name):
        '''transparent access to document subobjects
        '''
        try:
            data, mime = self.object.getSubObject(name)
        except AttributeError:
            pass
        else:
            return Wrapper(data, name, mime).__of__(self.context)
        return getattr(self, name)

    def publishTraverse(self, request, name):
        return self.__bobo_traverse__(request, name)
