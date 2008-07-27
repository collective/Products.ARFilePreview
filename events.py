# -*- coding: utf-8 -*-
#
# File: ARFilePreview/events.py
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

__author__ = u"""Jean-Nicolas Bès <contact@atreal.net>"""
__docformat__ = 'plaintext'
__licence__ = 'GPL'

from Acquisition import aq_base

from Products.ARFilePreview.interfaces import IPreviewable
import logging

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
        msg = "File on object %s has not changed ; no new preview" %( obj.getPhysicalPath())
        logger.log(logging.INFO, msg)
        return
    
    previewable = IPreviewable(obj)
    previewable.fileModified()
    isPreviewable = getattr(obj, 'isPreviewable', "always")
    if isPreviewable == "always":
        previewable.buildAndStorePreview()
    else:
        msg = "File's preview option is %s ; no new preview for %s " %( isPreviewable, obj.getPhysicalPath())  
