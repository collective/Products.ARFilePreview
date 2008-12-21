from Products.CMFCore.utils import UniqueObject
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName

from AccessControl import Unauthorized
from zExceptions import NotFound

from AccessControl import ClassSecurityInfo

##def wfsort(x, y):
##    if x['time'] > y['time']:
##        return 1
##    elif x['time'] == y['time']:
##        return 0
##    else:
##        return -1


class SpeedTool (UniqueObject, SimpleItem):
  """ SpeedTool  .... """
  id = 'speed_tool'
  meta_type= 'Speed Tool'
  plone_tool = 1
  
  security = ClassSecurityInfo()
  
  speedlink_prefix=""
  
  security.declarePublic('manage_transition')
  def manage_transition(self,speedfile):
    transition = speedfile.workflow_history['speedfile_workflow'][-1]['action']
    oldstate = speedfile.workflow_history['speedfile_workflow'][-2]['review_state']
    
    if transition=="submit":
        self.notify_reviewer(speedfile)
        
    elif transition=="publish":
        self.publish(speedfile)
        if oldstate=="pending":
            self.notify_author(speedfile, "published")
    
    elif transition=="retract":
        if oldstate=="published":
            self.unpublish(speedfile)
        
    elif transition=="reject":
        if oldstate=="published":
            self.unpublish(speedfile)
        self.notify_author(speedfile, "rejected")


  security.declarePublic('publish')
  def publish(self, speedfile):
    """ Publish """
    print "WF_DEBUG : publish(%s)" % (speedfile.getId())
    published_items = [speedfile]
    # Create a link in all related folders
    for ref in speedfile.getReferenceImpl(relationship='publishTo'):
      published_items.append(ref.create_link())
    # Notify all subscribers to the newly published items
    self.notify_subscribers(published_items)
  
  security.declarePublic('unpublish')
  def unpublish(self, speedfile):
    """ unPublish """
    print "WF_DEBUG : unpublish(%s)" % (speedfile.getId())
    # unlink in all related folders
    for ref in speedfile.getReferenceImpl(relationship='publishTo'):
      ref.delete_link()
 
  security.declarePublic('getExistingLinks')
  def getExistingLinks(self, speedfile):
    result = []
    for ref in speedfile.getReferenceImpl(relationship='publishTo'):
      try:
        link = ref.get_link()
      except AttributeError:
        # XXX old style reference.... this can be removed if
        # entire site is recreated
        link = None
      if link is not None:
        result.append(link)
    return result
    
  security.declarePublic('getExistingLinkUIDs')
  def getExistingLinkUIDs(self, speedfile):
    return [link.UID() for link in self.getExistingLinks(speedfile)]
    
  security.declarePublic('getpubinfos')
  def getpubinfos(self, speedlink):
    #if the speedlink arg doesn't have a portal_type attr or
    #if it's portal_type is not SpeedLink
    #raise an Unauthorized error
    #if not hasattr(speedlink, 'portal_type') or speedlink.portal_type!="SpeedLink":
    if getattr(speedlink, 'portal_type', None)!="SpeedLink":
      raise Unauthorized
    
    #get the object from it's UID
    uid_catalog=speedlink.uid_catalog
    brains=uid_catalog(UID=speedlink.getTargetUID())
    if len(brains)==0:
      #the link's target doesn't exists anymore
      raise NotFound
    speedfile = brains[0].getObject()
    
    #if the speedfile target doesn't have a portal_type attr or
    #if it's portal_type is not SpeedFile
    #raise an Unauthorized error
    if getattr(speedfile, 'portal_type', None)!="SpeedFile":
      raise Unauthorized
    
    wtool = getToolByName(speedlink, 'portal_workflow')
    review_state = wtool.getInfoFor(speedfile, 'review_state', '')
    if review_state!="published":
      raise Unauthorized
    infodict = {
      'title':            speedfile.Title() or speedfile.getId(),
      'subject':          speedfile.Sujet,
      'ref':              speedfile.Reference,
      'author':           speedfile.AuteurCreation,
      'publishdate':      speedfile.DateValidation,
      'description':      speedfile.Description(),
      'preview':          speedfile.getHTMLPreview(),
      'url':              speedfile.absolute_url(),
    }
    return infodict

  security.declarePrivate('notify_subscribers')
  def notify_subscribers(self, published_items):
    '''Notify all subscribers to the newly published items.

    The notification will be done in batch, so one
    user gets only one email during this operation,
    even if is subscribed to more folders.

    We suppose that the first item is the original speedfile
    where the rest are just links of the same.
    '''
    print "WF_DEBUG : notify_subscribers(%s)" % (published_items[0].getId())
    if not published_items:
      return
    pmt = getToolByName(self, 'portal_membership')
    mhost = getToolByName(self, 'MailHost')
    pprops = getToolByName(self, 'portal_properties')
    email_from_address = pprops.email_from_address
    # the message format, %s will be filled in from data
    message = """
    %(title)s
    URLs: %(urls)s
    """
    subject_txt = self.translate(
      domain='speed', 
      msgid='subscription_mail_subject', 
      default='Publication of subscribed item',
      )
    # build up a hash of who needs to be notified of what
    main_item = published_items[0]
    items_by_user = {}
    for item in published_items:
      if item.portal_type!="SpeedFolder":
        continue
      notify_users = item.getSubscribedUserIdsInherited()
      for user_id in notify_users:
        try:
          user_items = items_by_user[user_id]
        except KeyError:
          user_items = items_by_user[user_id] = []
        user_items.append(item)
    # now send out batch notifications  
    for user_id, items in items_by_user.iteritems():
      user = pmt.getMemberById(user_id)
      if user is not None and user.email:
        msg = message % dict(
          title = main_item.TitleOrId(),
          urls = ', '.join([item.absolute_url() for item in items]),
          )
        mhost.secureSend(msg,
            user.email,
            email_from_address,
            subject=subject_txt,
            subtype="plain",
            charset="utf-8")

  security.declarePublic('notify_author')
  def notify_author(self, main_item, state):
    '''Notify an author that it's item has been reviewed.
    '''
    print "WF_DEBUG : notify_author(%s, %s)" % (main_item.getId(), state)
    if not main_item:
      return
    pmt = getToolByName(self, 'portal_membership')
    mhost = getToolByName(self, 'MailHost')
    pprops = getToolByName(self, 'portal_properties')
    email_from_address = pprops.email_from_address
    # the message format, %s will be filled in from data
    message = """
    %(title)s
    URLs: %(url)s
    """
    if state=='published':
      subject_txt = self.translate(
        domain='speed', 
        msgid='notifyauthor_published_subject', 
        default='Your item has been published',
        )
    elif state=='rejected':
      subject_txt = self.translate(
        domain='speed',
        msgid='notifyauthor_rejected_subject',
        default='Your item has been rejected',
        )

        
    # now send out batch notifications  
    user = pmt.getMemberById(main_item.getOwner().getId())
    if user is not None and user.email:
      msg = message % dict(
        title = main_item.TitleOrId(),
        url = main_item.absolute_url(),
        )
      msg_subject = "%s - %s" % (subject_txt, main_item.TitleOrId())
      mhost.secureSend(msg,
                       user.email,
                       email_from_address,
                       subject=msg_subject,
                       subtype="plain",
                       charset="utf-8")
      #mhost.send(msg)

  security.declarePublic('notify_reviewer')
  def notify_reviewer(self, main_item):
    '''Notify an author that it's item has been reviewed.
    '''
    print "WF_DEBUG : notify_reviewer(%s)" % (main_item.getId())
    if not main_item:
      return
    pmt = getToolByName(self, 'portal_membership')
    mhost = getToolByName(self, 'MailHost')
    pprops = getToolByName(self, 'portal_properties')
    email_from_address = pprops.email_from_address
    # the message format, %s will be filled in from data
    message = """
    %(title)s
    URL: %(url)s
    """
    subject_txt = self.translate(
      domain='speed',
      msgid='notifyreviewer_pending_subject',
      default='An item is waiting for a review',
      )

        
    # now send out batch notifications  
    for user in pmt.listMembers():  
      if "Reviewer" in pmt.getMemberById(user.id).getRolesInContext(main_item):
        if user is not None and user.email:
          msg = message % dict(
            title = main_item.TitleOrId(),
            url = main_item.absolute_url(),
            )
          msg_subject = "%s - %s" % (subject_txt, main_item.TitleOrId())
          print "SEND("+user.id+"|"+user.email+")"
          print msg_subject
          mhost.secureSend(msg,
                           user.email,
                           email_from_address,
                           subject=msg_subject,
                           subtype="plain",
                           charset="utf-8")



  def updateAllPreviews(self):
    '''update the preview for all the speed files
    '''
    pc = getToolByName(self, 'portal_catalog')
    speedbrains = pc(portal_type='SpeedFile')
    status=""
    for brain in speedbrains:
      status+='''<div style="margin-top: 3em; border: 1px solid black; padding: 0.5em;">\n'''
      status+="<h2>%s</h2>\n" % (brain.getPath(),)
      print "UPDATE ALL PREVIEWS "+brain.getPath()
      try:
        obj=brain.getObject()
        obj.updatePreview()
        if hasattr(obj,'document_subobjects') and bool(obj.document_subobjects._subdict):
          status+='''<ul style="margin-left: 2em;">'''
          for key, val in obj.document_subobjects._subdict.items():
            status+="<li>%s (%d)</li>" % (key,len(val))
          status+="</ul>"
        else:
          status+='<div style="margin-left: 2em;">Pas de sous-objets</div>'
        obj.reindexObject()
      except Exception, e:
        status+="<b>%s %s</b></div>" % (str(e.__class__.__name__), str(e))
      else:
        status+=" OK</div>\n"
    return status

InitializeClass(SpeedTool)
