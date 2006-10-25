from Products.ARFilePreview.config import *
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.ARFilePreview.Extensions.utils import *
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

def install(self):
    out = StringIO()

    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)
    props = self.portal_properties.site_properties
    tabs = getattr(props, 'use_folder_tabs')
    contents = getattr(props, 'use_folder_contents')
    if 'Speed' not in tabs:
        newtabs = list(tabs)
        newtabs.append('Speed')
        props._updateProperty('use_folder_tabs', newtabs)
    if 'Speed' not in contents:
        newcontents = list(contents)
        newcontents.append('Speed')
        props._updateProperty('use_folder_contents', newcontents)
    
##    # create the extra roles
##    roles = ('SpeedAdmin', 'SpeedWriter')
##
##    for role in roles:
##        if role in self.__ac_roles__:
##            print >> out, 'Role "%s" is already set up in portal.' % role
##        else:
##            self._addRole(role)
##            print >> out, 'Setting up role "%s" in portal.' % role
##
##    #install the workflows
##    from Products.Speed.Extensions import speedfile_workflow
##    from Products.Speed.Extensions import speedfolder_workflow
##    
##    wf_tool = getToolByName(self, 'portal_workflow')
##    
##    if not 'speedfile_workflow' in wf_tool.objectIds():
##            wf_tool.manage_addWorkflow('speedfile_workflow (SpeedFile Workflow [SPEED])',
##                                       'speedfile_workflow')
##    if not 'speedfolder_workflow' in wf_tool.objectIds():
##            wf_tool.manage_addWorkflow('speedfolder_workflow (SpeedFolder Workflow [SPEED])',
##                                       'speedfolder_workflow')
##    
##    wf_tool.updateRoleMappings()
##    
##    #assign the workflows to the types
##    wf_tool.setChainForPortalTypes(pt_names=['SpeedFile'], 
##                                       chain='speedfile_workflow')
##    wf_tool.setChainForPortalTypes(pt_names=['SpeedFolder'], 
##                                       chain='speedfolder_workflow')
##    wf_tool.setChainForPortalTypes(pt_names=['SpeedLink'], 
##                                       chain='')

    #activate portal factory on the FilePreview content types
    pf_tool = getToolByName(self, 'portal_factory')
    factory_types = pf_tool.getFactoryTypes()
    factory_types['FilePreview'] = 1
    pf_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types.keys())
    
##    #register speed_tool with the plone site
##    if not hasattr(self, 'speed_tool'):
##      addTool = self.manage_addProduct[PROJECTNAME].manage_addTool
##      addTool('Speed Tool')
      
    #update content_type_registry to let speedfile handle text/* and application/* mimetypes
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

##    #install the SpeedSkin
##    setupSkins(self, out, SKINSELECTIONS, GLOBALS, SELECTSKIN, DEFAULTSKIN,
##                          ALLOWSELECTION, PERSISTENTCOOKIE)
##    registerStylesheets(self, out, STYLESHEETS)
##    registerScripts(self, out, JAVASCRIPTS)

    #install the Speed content skin
    install_subskin(self, out, globals=GLOBALS, skin_layers=["ARFilePreview"])
   
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    #remove the SpeedSkin
##    for skin in SKINSELECTIONS:
##        removeSkin(self, out, skin['name'], skin['base'], FULLRESET)
    #remove the Speed content skin
    uninstall_subskin(self, out, "ARFilePreview")
    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
