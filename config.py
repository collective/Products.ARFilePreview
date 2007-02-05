from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles
from Products.Archetypes.public import DisplayList

PROJECTNAME = 'ARFilePreview'

ADD_FILEPREVIEW_PERMISSION={}

ADD_FILEPREVIEW_PERMISSION['FilePreview'] = 'ARFilePreview: Add FilePreview'

setDefaultRoles ("ARFilePreview: Delete FilePreview", ('Manager', 'Owner', 'Author'))

SKINS_DIR='skins'
GLOBALS = globals()

