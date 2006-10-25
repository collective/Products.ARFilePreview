from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles
from Products.Archetypes.public import DisplayList

PROJECTNAME = 'ARFilePreview'

ADD_FILEPREVIEW_PERMISSION={}

ADD_FILEPREVIEW_PERMISSION['FilePreview'] = 'ARFilePreview: Add FilePreview'

setDefaultRoles ("ARFilePreview: Delete FilePreview", ('Manager','Author'))

SKINS_DIR='skins'
GLOBALS = globals()

#SKINSELECTIONS = (
#    {'name': 'FilePreviewSkin',
#     'base': 'Plone Default',
#     'layers': ('speed_skin',),
#     'selected': True,
#     },
#    )

SELECTSKIN = True
#DEFAULTSKIN = 'SpeedSkin'

STYLESHEETS = (
)

JAVASCRIPTS = ()


ALLOWSELECTION = False
PERSISTENTCOOKIE = False
FULLRESET = False
