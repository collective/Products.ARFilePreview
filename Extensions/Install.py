from Products.ARFilePreview.config import *
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.ARFilePreview.Extensions.utils import *
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

def install(self):
    out = StringIO()
    
    #install FilePreview type
    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)
    
    #activate portal factory on the FilePreview content types
    pf_tool = getToolByName(self, 'portal_factory')
    factory_types = pf_tool.getFactoryTypes()
    factory_types['FilePreview'] = 1
    pf_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types.keys())
    
    #update content_type_registry to let FilePreview handle text/* and application/* mimetypes
    ctr = getToolByName(self, 'content_type_registry')
    
    if 'application' not in ctr.predicate_ids:
        ctr.addPredicate('application', 'major_minor' )
        ctr.getPredicate('application').edit('application','')
    ctr.reorderPredicate('application', 0)
    ctr.assignTypeName('application', 'FilePreview')
    out.write('Installed CTR Predicate for handling WebDav puts of FilePreview content.\n')
    
    if 'text' not in ctr.predicate_ids:
        ctr.addPredicate('text', 'major_minor' )
        ctr.getPredicate('text').edit('text','')
    ctr.reorderPredicate('text', 1)
    ctr.assignTypeName('text', 'FilePreview')
    out.write('Installed CTR Predicate for handling WebDav puts of FilePreview content.\n')
    
    #install FilePreview's template directory
    install_subskin(self, out, globals=GLOBALS, skin_layers=["ARFilePreview"])
   
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    #remove FilePreview's template directory
    uninstall_subskin(self, out, "ARFilePreview")
    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
