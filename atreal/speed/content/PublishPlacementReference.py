
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.config import UID_CATALOG
from Products.Archetypes.exceptions import ReferenceException

class _marker:
    pass

class PublishPlacementReference(Reference):
    '''
    The reference is between a SpeedFile and a SpeedFolder.
    
    In the reference we store the UID of the actual link
    that (in case it is published) represents the proxied
    object.
    '''

    _uid_of_link = None

    speedlink_prefix = ''
    
    def _generate_link_id(self, speedfile, folder):
        'Generates a good link id'
        # Prefer to use a prefixed id.
        base_id = '%s%s' % (self.speedlink_prefix, speedfile.getId())
        if folder._getOb(base_id, _marker) == _marker:
            # Good, use this.
            return base_id
        # Attempt to put a postfix to the end.
        for i in range(1, 10000000):
          link_id = '%s_%i' % (base_id, i)
          if folder._getOb(link_id, _marker) == _marker:
              # Good, use this.
              return link_id
        raise Exception, 'Could not generate link id'

    def create_link(self):
        'Creates a link object in the folder'
        speedfile = self.getSourceObject()
        folder = self.getTargetObject()
        return self._create_link(speedfile, folder)

    def _create_link(self, speedfile, folder):
        link_id = self._generate_link_id(speedfile, folder)
        typestool = getToolByName(folder, 'portal_types')
        link_id = typestool.constructContent(type_name="SpeedLink", container=folder, 
            id=link_id, title=speedfile.TitleOrId(), targetUID=speedfile.UID(), description=speedfile.description)
        link = folder._getOb(link_id)
        self._uid_of_link = link.UID()
        link.reindexObject()
        return link

    def get_link(self):
        'Returns the link object or None'
        uid = self._uid_of_link
        if uid is None:
            return None
        tool = getToolByName(self, UID_CATALOG, None)
        if tool is None: 
            return None
        brains = tool(UID=uid)
        for brain in brains:
            obj = brain.getObject()
            if obj is not None:
                assert obj.meta_type == 'SpeedLink'
                return obj
        self._uid_of_link = None

    def delete_link(self):
        'Delete the link'
        link = self.get_link()
        if link is not None:
            try:
                link.aq_parent._delObject(link.getId())
            except (AttributeError, KeyError):
                # Huh... object gone, should not happen...
                pass
            self._uid_of_link = None

    # Hooks
    def addHook(self, tool, sourceObject=None, targetObject=None):
        # do not allow create a reference to the parent folder
        if sourceObject.aq_parent.aq_base == targetObject.aq_base:
            raise ReferenceException
        # if the speedfile is already published at this time, we must
        # create the link immediately.
        wft = getToolByName(tool, 'portal_workflow')
        state = wft.getInfoFor(sourceObject, 'review_state', default=None)
        if state == 'published':
            self._create_link(sourceObject, targetObject)

    def manage_beforeDelete(self, item, container):
        # if the reference gets deleted, make sure the object goes away
        self.delete_link()

