from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.ARFilePreview.config import PROJECTNAME,ADD_FILEPREVIEW_PERMISSION,SKINS_DIR,GLOBALS

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
  ##Import Types here to register them
  print "=================================================="
  print "atReal : ARFilePreview install in progress"
  from content import FilePreview

  content_types, constructors, ftis = process_types(
       listTypes(PROJECTNAME), PROJECTNAME)
  
  allTypes = zip(content_types, constructors)
  
  for atype, constructor in allTypes:
    print "atReal : initialize %s: %s" % (PROJECTNAME, atype.archetype_name)
    utils.ContentInit(
       "%s: %s" % (PROJECTNAME, atype.archetype_name),
       content_types      = (atype,),
       permission         = ADD_FILEPREVIEW_PERMISSION[atype.portal_type],
       extra_constructors = (constructor,),
       fti                = ftis,
       ).initialize(context)
  print "=================================================="
  
