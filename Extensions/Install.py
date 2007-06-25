# -*- coding: utf-8 -*-
#
# File: ARFilePreview/Extensions/Install.py
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


from StringIO import StringIO
from Products.ARFilePreview.config    import *
from Products.Archetypes.Extensions.utils import install_subskin

def install(self):
    """
    Install ARFilePreview
    """
    out = StringIO()
    pt = self.portal_types
    pt['File'].default_view = "file_preview"
    pt['File'].immediate_view = "file_preview"
    pt['File'].view_methods += ("file_preview", "file_asdoc")
    install_subskin(self, out, GLOBALS)
    print "installed ARFilePreview"
    return out.getvalue()


def uninstall(self):
    out = StringIO()
    pt = self.portal_types
    pt['File'].default_view = "file_view"
    pt['File'].immediate_view = "file_view"
    avViews = []
    for view in pt['File'].view_methods:
        if view in ["file_preview", "file_asdoc"]:
            continue
        avViews.append(view)
    pt['File'].view_methods = tuple(avViews)
    return out.getvalue()
