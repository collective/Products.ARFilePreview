from five import grok
from atreal.speed.content.interfaces import ISpeedFile, IMetadataExtractor
from Products.Archetypes.interfaces import IObjectInitializedEvent


@grok.subscribe(ISpeedFile, IObjectInitializedEvent)
def SpeedOnCreation(obj, event):

    meta = IMetadataExtractor(obj)
    idobj, fnum = meta.updateAydi()
    obj.getFile().filename = idobj
    meta.updateMetadata()
    meta.updateTitleFromMetas(fnum)

    print "updated metadata"
    obj.reindexObject()
