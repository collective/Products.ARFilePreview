# -*- coding: utf-8 -*-

from five import grok
from atreal.speed.content import interfaces as speed


class SpeedFileHandler(grok.Adapter):
    grok.context(speed.ISpeedFile)
    grok.implements(speed.ISpeedFileHandler)
    
    def manage_transition(self):
        transition = self.context.workflow_history['speedfile_workflow'][-1]['action']
        oldstate = self.context.workflow_history['speedfile_workflow'][-2]['review_state']
    
        if transition=="submit":
            self.notify_reviewer(self.context)
        
        elif transition=="publish":
            self.publish(self.context)
            if oldstate=="pending":
                self.notify_author(self.context, "published")
    
        elif transition=="retract":
            if oldstate=="published":
                self.unpublish(self.context)
        
        elif transition=="reject":
            if oldstate=="published":
                self.unpublish(self.context)
            self.notify_author(self.context, "rejected")


    def publish(self):
        published_items = [self.context]
        # Create a link in all related folders
        for ref in self.context.getReferenceImpl(relationship='publishTo'):
            published_items.append(ref.create_link())

        # Notify all subscribers to the newly published items
        self.notify_subscribers(published_items)
  

    def unpublish(self):
        for ref in self.context.getReferenceImpl(relationship='publishTo'):
            ref.delete_link()

 
    def getExistingLinks(self):
        result = []
        for ref in self.context.getReferenceImpl(relationship='publishTo'):
            try:
                link = ref.get_link()
            except AttributeError:
                # XXX old style reference.... this can be removed if
                # entire site is recreated
                link = None
            if link is not None:
                result.append(link)
        return result


    def getExistingLinkUIDs(self):
        return [link.UID() for link in self.getExistingLinks(self.context)]
