from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles
from Products.Archetypes.public import DisplayList

PROJECTNAME = 'Speed'

ADD_SPEED_PERMISSION={}

ADD_SPEED_PERMISSION['SpeedFile'] = 'Speed: Add SpeedFile'
ADD_SPEED_PERMISSION['SpeedFolder'] = 'Speed: Add SpeedFolder'
ADD_SPEED_PERMISSION['SpeedLink'] = 'Speed: Add SpeedLink'

setDefaultRoles ("Speed: Delete SpeedFile", ('Manager','SpeedAdmin'))

SKINS_DIR='skins'
GLOBALS = globals()

SKINSELECTIONS = (
    {'name': 'SpeedSkin',
     'base': 'Plone Default',
     'layers': ('speed_skin',),
#     'selected': True,
     },
    )

SELECTSKIN = True
DEFAULTSKIN = 'SpeedSkin'

STYLESHEETS = (
)

JAVASCRIPTS = ()


ALLOWSELECTION = False
PERSISTENTCOOKIE = False
FULLRESET = False
