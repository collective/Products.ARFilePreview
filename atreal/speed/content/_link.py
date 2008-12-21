# -*- coding: UTF-8 -*-

from Products.Archetypes.public import BaseContent
from schemas import SpeedLinkSchema


class SpeedLink(BaseContent):

    schema = BaseContent.schema.copy() + SpeedLinkSchema
    
