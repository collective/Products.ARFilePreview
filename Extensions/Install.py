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


import transaction
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Products.ARFilePreview.config    import *
from Products.Archetypes.Extensions.utils import install_subskin

PRODUCT_DEPENDENCIES = tuple()
EXTENSION_PROFILES = ('Products.ARFilePreview:default',)
UNINSTALL_PROFILES = tuple()

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

    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')

    for product in PRODUCT_DEPENDENCIES:
        is_installed = portal_quickinstaller.isProductInstalled(product)
        
        if reinstall and is_installed:
            portal_quickinstaller.reinstallProducts([product])
            transaction.savepoint()
            
        elif not is_installed:
            portal_quickinstaller.installProduct(product)
            transaction.savepoint()
        
    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id,
                                                  purge_old=False)
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()

    print "installed ARFilePreview"

    return "%s \nRan all install steps for." % out.getvalue()



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
    portal_setup = getToolByName(self, 'portal_setup')
    for extension_id in UNINSTALL_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id,
                                                  purge_old=False)
        transaction.savepoint()
        
    return "%s \nRan all uninstall steps for." % out.getvalue()

