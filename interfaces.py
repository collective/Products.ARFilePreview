# -*- coding: utf-8 -*-
#
# File: ARFilePreview/interfaces.py
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


from zope.interface import Interface
from zope.app.event.interfaces import IObjectModifiedEvent


class IPreviewAware( Interface ):
    """ marker interface """

class IPreviewable( Interface ):
    
    def hasPreview( ):
        """
        Has the preview
        """
    
    def setPreview( preview):
        """
        Sets the preview
        """
    
    def getPreview( ):
        """
        Get the preview
        """
   
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
    
    def updateAllPreviews( ):
        """
        update all the previews reachable from the catalog
        """
