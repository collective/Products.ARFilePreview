
from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from sets import Set

class SubscriptionSupport:
    '''Mixin for subscription support
    '''

    security = ClassSecurityInfo()

    # Storage is accessed like in AT but we
    # really don't need AT at the moment

    security.declareProtected(permissions.View, 'getSubscribedUserIds')
    def getSubscribedUserIds(self):
        '''Returns user ids subscribed locally
        '''
        try:
            return self.aq_base.subscribedUserIds
        except AttributeError:
            return ()

    security.declareProtected(permissions.ModifyPortalContent, 'setSubscribedUserIds')
    def setSubscribedUserIds(self, value):
        '''Sets user ids subscribed locally
        '''
        assert isinstance(value, (tuple, list))
        self.subscribedUserIds = tuple(value)

    security.declareProtected(permissions.View, 'getSubscribedUserIdsInherited')
    def getSubscribedUserIdsInherited(self):
        '''Returns user ids subscribed locally or to any of the parent folders

        result order can be arbitrary
        '''
        result = self.getSubscribedUserIds()
        try:
            method = self.aq_parent.getSubscribedUserIds
        except (AttributeError, IndexError):
            pass
        else:
            more_ids = method()
            result = tuple(Set(result).union(more_ids))
        return result

    # --
    # Management of subscriptions
    # --
    
    security.declareProtected(permissions.ModifyPortalContent, 'getUserSubscribedInfo')
    def getUserSubscribedInfo(self, user):
        '''Returns user subscription information
        
        returns dict with keys 'inherited', 'local' subscription status
        '''
        info = {
            'local': self.getUserSubscribed(user),
            'inherited': self._getUserSubscribedInheritedFromParent(user),
            }
        return info
        
    security.declareProtected(permissions.ModifyPortalContent, 'getUserSubscribedInherited')
    def getUserSubscribedInherited(self, user):
        '''Returns if a user is subscribed locally or to any of the parent folders
        '''
        local_stat = self.getUserSubscribed(user)
        if local_stat:
            return True
        else:
            return self._getUserSubscribedInheritedFromParent(user)

    def _getUserSubscribedInheritedFromParent(self, user):
        try:
            method = self.aq_parent.getUserSubscribedInherited
        except (AttributeError, IndexError):
            inherited_stat = False
        else:
            inherited_stat = method(user)
        return inherited_stat
        
    security.declareProtected(permissions.ModifyPortalContent, 'getUserSubscribed')
    def getUserSubscribed(self, user):
        '''Returns if a user is subscribed locally to this object
        '''
        if not isinstance(user, basestring):
            user_id = user.getId()
        else:
            user_id = user
        is_subscribed = user_id in self.getSubscribedUserIds()
        return bool(is_subscribed) 
        
    security.declareProtected(permissions.ModifyPortalContent, 'setUserSubscribed')
    def setUserSubscribed(self, user, value):
        '''Set a user's local subscription status
        '''
        if not isinstance(user, basestring):
            user_id = user.getId()
        else:
            user_id = user
        old_value = list(self.getSubscribedUserIds())
        is_subscribed = user_id in old_value
        if value and not is_subscribed:
            old_value.append(user_id)
            self.setSubscribedUserIds(old_value)
        elif not value and is_subscribed:
            old_value.remove(user_id)
            self.setSubscribedUserIds(old_value)
        
    # --
    # Active user
    # --
    
    security.declareProtected(permissions.View, 'getActiveSubscribedInfo')
    def getActiveSubscribedInfo(self):
        '''Returns subscription information for the active user
        
        returns dict with keys 'inherited', 'local' subscription status
        '''
        pmt = getToolByName(self, 'portal_membership')
        user = pmt.getAuthenticatedMember()
        info = {
            'local': self.getUserSubscribed(user),
            'inherited': self._getUserSubscribedInheritedFromParent(user),
            }
        return info
        
    security.declareProtected(permissions.View, 'getActiveSubscribed')
    def getActiveSubscribed(self):
        '''Returns if the active user is subscribed locally'''
        pmt = getToolByName(self, 'portal_membership')
        user = pmt.getAuthenticatedMember()
        return self.getUserSubscribed(user)
        
    security.declareProtected(permissions.View, 'getActiveSubscribed')
    def getActiveSubscribedInherited(self):
        '''Returns if the active user is subscribed locally or to any parent folders'''
        pmt = getToolByName(self, 'portal_membership')
        user = pmt.getAuthenticatedMember()
        return self.getUserSubscribedInherited(user)
        
    security.declareProtected(permissions.View, 'setActiveSubscribed')
    def setActiveSubscribed(self, value):
        '''Sets subscription state of the active user on this object

        Since the user can modify this by himself on the objects he sees,
        View permission would be sufficient for this method.
        '''
        pmt = getToolByName(self, 'portal_membership')
        user = pmt.getAuthenticatedMember()
        self.setUserSubscribed(user, value)

    # --
    # View methods
    # --

    security.declareProtected(permissions.View, 'computeUsersSubscription')
    def computeUsersSubscription(self):
        pmt = getToolByName(self, 'portal_membership')
        # First decide if we are an admin at all.
        user = pmt.getAuthenticatedMember()
        roles = user.getRolesInContext(self)
        if not ('Owner' in roles or 'Manager' in roles):
            # Sorry, no privilege
            return None
        # We are priviledged, compute our information
        subscribed, unsubscribed = [], []
        for user in pmt.listMembers():
            subscribed_info = self.getUserSubscribedInfo(user)
            if subscribed_info['local'] or subscribed_info['inherited']:
                subscribed.append(dict(
                    user_id = user.getId(),
                    local = subscribed_info['local'],
                    inherited = subscribed_info['inherited'],
                    ))
            else:
                unsubscribed.append(user.getId())
        return dict(subscribed=subscribed, unsubscribed=unsubscribed)
