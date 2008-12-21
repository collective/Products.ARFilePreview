
from Products.Archetypes.tests.ArchetypesTestCase import *
from Products.PloneTestCase import PloneTestCase
from Products.Archetypes.public import *
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from sets import Set
from Products.Speed.content.PublishPlacementReference import PublishPlacementReference

PloneTestCase.installProduct('Speed')

class TestPublicationLinking(ArcheSiteTestCase):
    
    RELNAME = 'publishTo'

    def afterSetUp(self):
        # Adds the product
        self.addProduct('Speed')
        # assume manager for all tests
        self.setRoles(['Manager'])
        # create some objects
        self.f1 = _createObjectByType('SpeedFolder', self.portal, 'f1')
        self.f2 = _createObjectByType('SpeedFolder', self.portal, 'f2')
        self.f3 = _createObjectByType('SpeedFolder', self.portal, 'f3')
        self.f4 = _createObjectByType('SpeedFolder', self.portal, 'f4')
        self.f5 = _createObjectByType('SpeedFolder', self.portal, 'f5')
        self.f6 = _createObjectByType('SpeedFolder', self.portal, 'f6')
        
    def beforeTearDown(self):
        pass
    
    def createSpeedFile(self, f, id):
        # Must set metadata in order to make object publishable
        return _createObjectByType('SpeedFile', f, id,
            OriginalFile = 'X', Contexte = 'X', Sujet = 'X', Reference = 'X',
            Version = 'X', DateCreation = '2006/01/01', AuteurCreation = '2006/01/01',
            DateValidation = '2006/01/01', Valideurs = 'X',
            )

    def assertSameSet(self, s1, s2):
        s1 = Set([o.UID() for o in s1])
        s2 = Set([o.UID() for o in s2])
        self.assertEqual(s1, s2)
        
    def assertContentIds(self, f, ids):
        s1 = Set(f.objectIds())
        s2 = Set(ids)
        self.assertEqual(s1, s2)

    def testAdding(self):
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2])
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # double adding does not double it and does not raise error
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # removing
        o1.deleteReference(f2, relationship=RELNAME)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f3])
        
    def testNoAddingToItself(self):
        'linking: no adding to itself'
        f1 = self.f1
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f1, relationship=RELNAME, referenceClass=PublishPlacementReference)
        # nothing happened... but it is not there.
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [])
        
    def testPublishing(self):
        'linking: publishing' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2])
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # publish the object
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertEqual(f2.o1.meta_type, 'SpeedLink')
        self.assertContentIds(f3, ['o1'])
        self.assertEqual(f3.o1.meta_type, 'SpeedLink')
        # unpublish the object
        wft.doActionFor(o1, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, [])
        self.assertContentIds(f3, [])

    def testPublishingAndAfter(self):
        'linking: publishing and change refstate' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        f4 = self.f4
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # publish the object
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1'])
        # add another ref
        o1.addReference(f4, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertContentIds(f4, ['o1'])
        self.assertEqual(f4.o1.meta_type, 'SpeedLink')
        # double adding does not matter!
        o1.addReference(f4, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertContentIds(f4, ['o1'])
        # remove a ref
        o1.deleteReference(f2, relationship=RELNAME)
        self.assertContentIds(f2, [])
        # unpublish the object
        wft.doActionFor(o1, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, [])
        self.assertContentIds(f3, [])
        self.assertContentIds(f4, [])
        
    def testPublishingAndDoubleAdding(self):
        'linking: publishing and double adding' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # publish the object
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1'])
        # double add a ref
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertContentIds(f3, ['o1'])
        self.assertEqual(f3.o1.meta_type, 'SpeedLink')

    def testDeletingLink(self):
        'linking: deleting the link' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # publish the object
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1'])
        # delete a link
        f3._delObject('o1')
        # retract
        wft.doActionFor(o1, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, [])
        self.assertContentIds(f3, [])
 
    def testMovingLink(self):
        'linking: moving the link' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # publish the object
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1'])
        # move a link
        moving = f3.o1.aq_base
        f3._delObject('o1')
        moving.setId('oX')
        f2._setObject('oX', moving)
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1', 'oX'])
        self.assertContentIds(f3, [])
        # retract
        wft.doActionFor(o1, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, [])
        self.assertContentIds(f3, [])
        
    def testRenamingLink(self):
        'linking: renaming the link' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o1.addReference(f2, relationship=RELNAME, referenceClass=PublishPlacementReference)
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f2, f3])
        # publish the object
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1'])
        # move a link
        moving = f3.o1.aq_base
        f3._delObject('o1')
        moving.setId('oX')
        f3._setObject('oX', moving)
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['oX'])
        # retract
        wft.doActionFor(o1, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, [])
        self.assertContentIds(f3, [])
        
    def testIdNoClash(self):
        'linking: ids do not clash' 
        wft = self.portal.portal_workflow
        f1 = self.f1
        f2 = self.f2
        f3 = self.f3
        RELNAME = self.RELNAME
        o1 = self.createSpeedFile(f1, 'o1')
        o2 = self.createSpeedFile(f2, 'o1')
        o1.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        o2.addReference(f3, relationship=RELNAME, referenceClass=PublishPlacementReference)
        self.assertSameSet(o1.getReferences(relationship=RELNAME), [f3])
        self.assertSameSet(o2.getReferences(relationship=RELNAME), [f3])
        # publish the objects
        wft.doActionFor(o1, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1'])
        wft.doActionFor(o2, 'publish')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1', 'o1_1'])
        # retract
        wft.doActionFor(o1, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, ['o1_1'])
        wft.doActionFor(o2, 'retract')
        self.assertContentIds(f1, ['o1'])
        self.assertContentIds(f2, ['o1'])
        self.assertContentIds(f3, [])
 
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPublicationLinking))
    return suite
