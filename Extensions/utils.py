from Globals import package_home
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.utils import getToolByName
import os, string


def getSkinsFolderNames(globals, skins_dir='skins'):
    # Get the content of the skins folder
    skins_path = os.path.join(package_home(globals), skins_dir)
    return [ filename for filename in os.listdir(skins_path)
        if (not filename.startswith('.') or filename in ('CVS', '{arch}'))
        and os.path.isdir(os.path.join(skins_path, filename)) ]

def setupSkin(self, out, skin_selection, globals, make_default,
                         allow_any, cookie_persistence):
    skins_tool = getToolByName(self, 'portal_skins')
    skin_name, base_skin = skin_selection['name'], skin_selection['base']

    # Only add the skin selection if it doesn't already exist
    if skin_name not in skins_tool.getSkinSelections():

        # Get the skin layers of the base skin and convert to an array
        layers = skins_tool.getSkinPath(base_skin)
        layers = map(string.strip, string.split(layers, ','))

        # Add the skin folders to the layers, under 'custom'
        filenames = skin_selection.get('layers', getSkinsFolderNames(globals))
        for filename in filenames:
            if filename not in layers:
                try:
                    layers.insert(layers.index('custom')+1, filename)
                except ValueError:
                    layers.insert(0, filename)

        # Add our skin selection
        layers = ', '.join(layers)
        skins_tool.addSkinSelection(skin_name, layers)
        print >> out, "Added skin selection to portal_skins."

        # Activate the skin selection
        if make_default:
            skins_tool.default_skin = skin_name

        # Setup other tool properties
        skins_tool.allow_any = allow_any
        skins_tool.cookie_persistence = cookie_persistence

    else:
        print >> out, "Skin selection already exists, leaving it alone."

def setupSkins(self, out, skin_selections, globals, select_skin, default_skin,
                          allow_any, cookie_persistence, skins_dir='skins'):
    skins_tool = getToolByName(self, 'portal_skins')

    # Add directory views
    addDirectoryViews(skins_tool, skins_dir, globals)
    print >> out, "Added directory views to portal_skins."

    # Install skin selections
    for skin in skin_selections:
        make_default = False
        if select_skin and skin['name'] == default_skin:
            make_default = True
        setupSkin(self, out, skin, globals, make_default,
                                   allow_any, cookie_persistence)

def registerStylesheets(self, out, stylesheets):
    # register additional CSS stylesheets with portal_css
    csstool = getToolByName(self, 'portal_css')
    for css in stylesheets:
        csstool.registerStylesheet(**css)
    print >> out, "installed the Plone additional stylesheets."

def registerScripts(self, out, scripts):
    # register additional JS Scripts with portal_javascripts
    jstool = getToolByName(self, 'portal_javascripts')
    for js in scripts:
        jstool.registerScript(**js)
    print >> out, "installed the Plone additional javascripts."

def removeSkin(self, out, skin_name, base_skin, fullreset):
    # Delete the portal_skins property which holds the skin selection
    skins_tool = getToolByName(self, 'portal_skins')
    if skin_name in skins_tool.getSkinSelections():
        # Remove skin selection from portal_skins
        skins_tool.manage_skinLayers(del_skin=1, chosen=(skin_name,))
        if fullreset:
            # Restore Plone defaults
            skins_tool.allow_any = 0
            skins_tool.cookie_persistence = 0
            skins_tool.default_skin = 'Plone Default'
        else:
            # Restore the base skin as default one
            skins_tool.default_skin = base_skin
        print >> out, "Removed skin selection from portal skins."


from Products.Archetypes import types_globals
from Products.CMFCore.utils import minimalpath
from Products.CMFCore.DirectoryView import addDirectoryViews, \
     registerDirectory, manage_listAvailableDirectories
from OFS.ObjectManager import BadRequestException
from os.path import isdir, join


def install_subskin(self, out, globals=types_globals, product_skins_dir='skins', skin_layers=None):
    skinstool=getToolByName(self, 'portal_skins')

    fullProductSkinsPath = os.path.join(package_home(globals), product_skins_dir)
    productSkinsPath = minimalpath(fullProductSkinsPath)
    registered_directories = manage_listAvailableDirectories()
    if productSkinsPath not in registered_directories:
        try:
            registerDirectory(product_skins_dir, globals)
        except OSError, ex:
            if ex.errno == 2: # No such file or directory
                return
            raise
    try:
        addDirectoryViews(skinstool, product_skins_dir, globals)
    except BadRequestException, e:
        # XXX: find a better way to do this, but that seems not feasible
        #      until Zope stops using string exceptions
        if str(e).endswith(' is reserved.'):
            # trying to use a reserved identifier, let the user know
            #
            # remember the cmf reserve ids of objects in the root of the
            # portal !
            raise
        # directory view has already been added
        pass

    files = os.listdir(fullProductSkinsPath)
    for productSkinName in files:
        if (skin_layers is not None) and (productSkinName not in skin_layers):
            continue
        # skip directories with a dot or special dirs
        # or maybe just startswith('.')?
        if productSkinName.find('.') != -1 or productSkinName in ('CVS', '{arch}'):
            continue
        if isdir(join(fullProductSkinsPath, productSkinName)):
            for skinName in skinstool.getSkinSelections():
                path = skinstool.getSkinPath(skinName)
                path = [i.strip() for i in  path.split(',')]
                try:
                    if productSkinName not in path:
                        path.insert(path.index('custom') +1, productSkinName)
                except ValueError:
                    if productSkinName not in path:
                        path.append(productSkinName)
                path = ','.join(path)
                skinstool.addSkinSelection(skinName, path)

def uninstall_subskin(self, out, skinlayer):
    skinstool=getToolByName(self, 'portal_skins')
    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        layers_list = [i.strip() for i in  path.split(',')]
        if skinlayer in layers_list:
            layers_list.remove(skinlayer)
        else:
            print "Warning: '"+skinlayer+"' layer already removed from '"+skinName+"' skin"
        path = ','.join(layers_list)
        skinstool.addSkinSelection(skinName, path)

__all__ = (
    "setupSkins",
    "registerStylesheets",
    "registerScripts",
    "removeSkin",
    "install_subskin",
    "uninstall_subskin",
        )
