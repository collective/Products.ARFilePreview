# -*- coding: utf-8 -*-

project = "atreal.speed"

from five import grok
from Products.CMFCore import utils
from Products.Archetypes import atapi
from Products.Archetypes.public import registerType
from atreal.speed.content import SpeedFile, SpeedFolder, SpeedLink
from atreal.speed.security.permissions import *


registerType(SpeedFile, project)
registerType(SpeedFolder, project)
registerType(SpeedLink, project)

ADD_PERMISSIONS = {
    "SpeedFile": AddFile,
    "SpeedFolder" : AddFolder,
    "SpeedLink": AddLink
    }


def RegisterContent(context):
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(project), project
        )

    for atype, constructor in zip(content_types, constructors):
        permission = ADD_PERMISSIONS[atype.portal_type]
        utils.ContentInit('%s: %s' % (project, atype.portal_type),
            content_types      = (atype,),
            permission         = grok.title.bind().get(permission),
            extra_constructors = (constructor,),
            ).initialize(context)
