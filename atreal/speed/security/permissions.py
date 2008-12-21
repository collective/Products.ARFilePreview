# -*- coding: utf-8 -*-

from five import grok


class AddFile(grok.Permission):
    grok.name('atreal.speed.AddFile')
    grok.title('atreal.speed: Add SpeedFile')
    
class DeleteFile(grok.Permission):
    grok.name('atreal.speed.DeleteFile')
    grok.title('atreal.speed: Delete SpeedFile')

class AddFolder(grok.Permission):
    grok.name('atreal.speed.AddFolder')
    grok.title('atreal.speed: Add SpeedFolder')

class AddLink(grok.Permission):
    grok.name('atreal.speed.AddLink')
    grok.title('atreal.speed: Add SpeedLink')


__all__ = ("AddFile", "AddFolder", "AddLink")
