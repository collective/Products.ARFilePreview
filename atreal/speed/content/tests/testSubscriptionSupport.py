
from Products.Archetypes.tests.ArchetypesTestCase import *
from Products.Archetypes.tests.common import mkDummyInContext
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.Speed.content.SubscriptionSupport import SubscriptionSupport
from sets import Set

class TestFolder(SubscriptionSupport, BaseFolder):
    pass
    
class TestSubscriptionSupport(ArcheSiteTestCase):
    
    def afterSetUp(self):
        self.f1 = mkDummyInContext(TestFolder, 'sub', self.folder)
        self.f2 = mkDummyInContext(TestFolder, 'sub', self.f1)
        pmt = getToolByName(self.portal, 'portal_membership')
        pmt.addMember('user2', 'secret', (), ())
        self.user2 = pmt.getMemberById('user2')
        
    def beforeTearDown(self):
        pass
                                  
    def testSetting(self):
        'subscriptionsupport: Setting up subscription'
        self.setRoles(['Manager'])
        f2 = self.f2
        # originally empty
        self.assertEqual(f2.getSubscribedUserIds(), ())
        # setting and retrieving
        f2.setSubscribedUserIds(('test_user_1_', 'user2'))
        self.assertEqual(f2.getSubscribedUserIds(), ('test_user_1_', 'user2'))
        # must set a list or tuple
        self.assertRaises(AssertionError, f2.setSubscribedUserIds, 'NotATuple')
        
    def testSettingNoAcquisition(self):
        'subscriptionsupport: Setting up subscription, acquisition ok'
        self.setRoles(['Manager'])
        f2 = self.f2
        f1 = self.f1
        # setting and retrieving
        f1.setSubscribedUserIds(('test_user_1_', 'user2'))
        self.assertEqual(f2.getSubscribedUserIds(), ())
        
    def testSettingInherited(self):
        'subscriptionsupport: Setting up subscription, inherited get'
        self.setRoles(['Manager'])
        f2 = self.f2
        f1 = self.f1
        # setting and retrieving
        f1.setSubscribedUserIds(('user2', ))
        f2.setSubscribedUserIds(('test_user_1_', 'user2'))
        self.assertEqual(Set(f2.getSubscribedUserIdsInherited()), Set(('test_user_1_', 'user2')))
        # setting and retrieving
        f1.setSubscribedUserIds(('test_user_1_', 'user2'))
        f2.setSubscribedUserIds(('user2', ))
        self.assertEqual(Set(f2.getSubscribedUserIdsInherited()), Set(('test_user_1_', 'user2')))
        
    def testPerUser(self):
        'subscriptionsupport: Setting up per-user logic'
        self.setRoles(['Manager'])
        f2 = self.f2
        # originally empty
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), False)
        self.assertEqual(f2.getUserSubscribed('user2'), False)
        # setting a value
        f2.setUserSubscribed('user2', True)
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), False)
        self.assertEqual(f2.getUserSubscribed('user2'), True)
        f2.setUserSubscribed('user2', True)
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), False)
        self.assertEqual(f2.getUserSubscribed('user2'), True)
        f2.setUserSubscribed('user2', False)
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), False)
        self.assertEqual(f2.getUserSubscribed('user2'), False)
        f2.setUserSubscribed('user2', False)
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), False)
        self.assertEqual(f2.getUserSubscribed('user2'), False)
        
    def testUserObjects(self):
        'subscriptionsupport: Setting up per-user, by objects'
        self.setRoles(['Manager'])
        f2 = self.f2
        f2.setUserSubscribed(self.user2, True)
        self.assertEqual(f2.getUserSubscribed('user2'), True)

    def testPerUserInherited(self):
        'subscriptionsupport: per-user inheritence'
        self.setRoles(['Manager'])
        f2 = self.f2
        f1 = self.f1
        # originally empty
        self.assertEqual(f2.getUserSubscribedInherited('user2'), False)
        self.assertEqual(f2.getUserSubscribedInfo('user2'), {'local': False, 'inherited': False})
        # setting a value
        f2.setUserSubscribed('user2', True)
        self.assertEqual(f2.getUserSubscribedInherited('user2'), True)
        self.assertEqual(f2.getUserSubscribedInfo('user2'), {'local': True, 'inherited': False})
        # setting inheritence
        f1.setUserSubscribed('user2', True)
        self.assertEqual(f2.getUserSubscribedInherited('user2'), True)
        self.assertEqual(f2.getUserSubscribedInfo('user2'), {'local': True, 'inherited': True})
        # unsetting a local value
        f2.setUserSubscribed('user2', False)
        self.assertEqual(f2.getUserSubscribedInherited('user2'), True)
        self.assertEqual(f2.getUserSubscribedInfo('user2'), {'local': False, 'inherited': True})
        # unsetting inheritence
        f1.setUserSubscribed('user2', False)
        self.assertEqual(f2.getUserSubscribedInherited('user2'), False)
        self.assertEqual(f2.getUserSubscribedInfo('user2'), {'local': False, 'inherited': False})
        
    def testActive(self):
        'subscriptionsupport: active user'
        f2 = self.f2
        f1 = self.f1
        # Setting initially
        self.assertEqual(f2.getActiveSubscribed(), False)
        self.assertEqual(f2.getActiveSubscribedInherited(), False)
        self.assertEqual(f2.getActiveSubscribedInfo(), {'local': False, 'inherited': False})
        # Can set up, only vith View permission.
        f2.setActiveSubscribed(True)
        self.assertEqual(f2.getActiveSubscribed(), True)
        self.assertEqual(f2.getActiveSubscribedInherited(), True)
        self.assertEqual(f2.getActiveSubscribedInfo(), {'local': True, 'inherited': False})
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), True)
        # Can set up, only vith View permission.
        f1.setActiveSubscribed(True)
        self.assertEqual(f2.getActiveSubscribed(), True)
        self.assertEqual(f2.getActiveSubscribedInherited(), True)
        self.assertEqual(f2.getActiveSubscribedInfo(), {'local': True, 'inherited': True})
        # Can set up, only vith View permission.
        f2.setActiveSubscribed(False)
        self.assertEqual(f2.getActiveSubscribed(), False)
        self.assertEqual(f2.getActiveSubscribedInherited(), True)
        self.assertEqual(f2.getActiveSubscribedInfo(), {'local': False, 'inherited': True})
        # Can set up, only vith View permission.
        f1.setActiveSubscribed(False)
        self.assertEqual(f2.getActiveSubscribed(), False)
        self.assertEqual(f2.getActiveSubscribedInherited(), False)
        self.assertEqual(f2.getActiveSubscribedInfo(), {'local': False, 'inherited': False})
        self.assertEqual(f2.getUserSubscribed('test_user_1_'), False)
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubscriptionSupport))
    return suite
