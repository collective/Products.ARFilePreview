# -*- coding: utf-8 -*-

from five import grok
from zope.event import notify
from zope.formlib import form
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.app.form.events import EditCancelledEvent, EditSavedEvent
from Products.CMFPlone import PloneMessageFactory as __
from atreal.filepreview import interfaces
from Products.CMFPlone.Portal import PloneSite

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("arfilepreview")


grok.templatedir("templates")


class GlobalConfigurationForm(grok.EditForm):
    """Editing the global configuration
    """
    grok.name("global_preview_configuration")
    grok.require("cmf.ManagePortal")
    grok.context(PloneSite)
    grok.template('formconfiglet')
    
    # For the form details
    label = _(u"arpreviewfile_global_configuration",
              default=u"Global preview configuration")
    
    form_name = _(u"arpreviewfile_global_configuration_name",
                  default=u"Configuration options")
    
    # About the fields
    form_fields = form.FormFields(interfaces.IGlobalPreviewConfiguration)


    @form.action(_(u"label_change_configuration",
                   default="Update configuration"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
            self.status = "Changes saved"
        else:
            self.status = "No changes"


    @form.action(__(u"label_cancel", default=u"Cancel"), name=u'cancel')
    def handle_cancel_action(self, action, data):
        return self.next_url(target="/plone_control_panel")


    @form.action(_(u"label_update_allpreviews",
                   default="Update all previews"),
                 condition=form.haveInputWidgets,
                 name=u'updateallpreviews')
    def handle_updateall(self, action, data):
        error, status = getUtility(interfaces.IGlobalPreviewHandler).updateAllPreviews(self.context)
        if not error:
            self.status = u"Previews successfully updated."
        else:
            self.status = u"There was some errors while processing. Please check the logs."
            self.errors = True
            
            
    @form.action(_(u"label_update_newpreview",
                   default="Update new previews"),
                 condition=form.haveInputWidgets,
                 name=u'updatenewpreviews')
    def handle_updatenew(self, action, data):
        error, status = getUtility(interfaces.IGlobalPreviewHandler).updateNewPreviews(self.context)
        if not error:
            self.status = u"Previews successfully updated."
        else:
            self.status = u"There was some errors while processing. Please check the logs."
            self.errors = True


    def next_url(self, target=None):
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + (target or '/view'))
