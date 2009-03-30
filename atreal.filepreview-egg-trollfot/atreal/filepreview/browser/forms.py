# -*- coding: utf-8 -*-

from five import grok
from zope.event import notify
from zope.formlib import form
from zope.component import getMultiAdapter
from plone.app.form.events import EditCancelledEvent, EditSavedEvent
from Products.CMFPlone import PloneMessageFactory as __
from atreal.filepreview import interfaces
from Products.CMFPlone.Portal import PloneSite

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("arfilepreview")


grok.templatedir("templates")

class ConfigurationForm(grok.EditForm):
    """Editing the configuration
    """
    grok.name("file_preview_configuration")
    grok.require("cmf.ModifyPortalContent")
    grok.context(interfaces.IPreviewAware)
    grok.template('form')
    
    # For the form details
    label = _(u"arpreviewfile_configuration",
              default=u"Preview configuration")
    
    form_name = _(u"arpreviewfile_configuration_name",
                  default=u"Preferences of the preview generation")
    
    # About the fields
    form_fields = form.FormFields(interfaces.IPreviewConfiguration)

    def next_url(self, target=None):
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + (target or '/view'))

    @form.action(_(u"label_change_configuration",
                   default="Update configuration"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields,
                             data, self.adapters):
            # here trigger the event !!
            # notify(PreviewConfigurationChanged(self.context, data))
            notify(EditSavedEvent(self.context))
            self.status = "Changes saved"
        else:
            notify(EditCancelledEvent(self.context))
            self.status = "No changes"
            
        return self.next_url()

    @form.action(__(u"label_cancel", default=u"Cancel"), name=u'cancel')
    def handle_cancel_action(self, action, data):
        notify(EditCancelledEvent(self.context))
        return self.next_url()


class GlobalConfigurationForm(ConfigurationForm):
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
