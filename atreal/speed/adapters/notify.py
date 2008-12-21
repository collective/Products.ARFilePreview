# -*- coding: utf-8 -*-

from five import grok
from atreal.speed.content import interfaces as speed


class Notifier(grok.GlobalUtility):

    grok.name("atreal.speed.utility")
    grok.implements(speed.ISpeedNotifier)

    
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


        def notify_author(self, main_item, state):
            """Notify an author that it's item has been reviewed.
            """
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


        def notify_reviewer(self, main_item):
            """Notify an author that it's item has been reviewed.
            """
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
