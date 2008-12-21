#-*- coding: UTF-8 -*-

from Products.Archetypes.public import *
from PublishPlacementReference import PublishPlacementReference
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import relatedItemsField


SpeedLinkSchema = Schema((
    
    StringField('targetUID',
        default='',
        widget=StringWidget(
            label='Identifiant Cible',
            invisible = {'view': "invisible", 'edit': "invisible"}
        ),
    ),
))


SpeedFileSchema = Schema((

        StringField ('Contexte',
                     searchable=1,
                     isMetadata=1,
                     required=1,
                     schemata="metadata",
                     speedmeta=1,
                     default='',
                     widget=StringWidget(label='Contexte')),
        
        StringField('Sujet',
                    searchable=1,
                    required=1,
                    isMetadata=1,
                    schemata="metadata",
                    speedmeta=1,
                    default='',
                    widget=StringWidget(label='Sujet')),
        
        StringField('Reference',
                    searchable=1,
                    required=1,
                    isMetadata=1,
                    speedmeta=1,
                    schemata="metadata",
                    default='',
                    widget=StringWidget(label='Reference')),
        
        StringField('Version',
                    searchable=1,
                    required=1,
                    isMetadata=1,
                    speedmeta=1,
                    schemata="metadata",
                    default='',
                    widget=StringWidget(label='Version')),
        
        DateTimeField('DateCreation',
                      searchable=1,
                      required=1,
                      isMetadata=1,
                      speedmeta=1,
                      schemata="metadata",
                      default='',
                      widget=CalendarWidget(label='Date de Creation')),
        
        StringField('AuteurCreation',
                     searchable=1,
                     required=1,
                     isMetadata=1,
                     speedmeta=1,
                     schemata="metadata",
                     default='',
                     widget=StringWidget(label='Createur(s)')),
        
        DateTimeField('DateModification',
                      searchable=1,
                      required=0,
                      isMetadata=1,
                      speedmeta=1,
                      schemata="metadata",
                      default='',
                      widget=CalendarWidget(label='Date de Modification')),
        
        StringField('AuteurModification',
                    searchable=1,
                    required=0,
                    isMetadata=1,
                    speedmeta=1,
                    schemata="metadata",
                    default='',
                    widget=StringWidget(label='Modifié par')),
        
        DateTimeField('DateValidation',
                      searchable=1,
                      required=1,
                      isMetadata=1,
                      speedmeta=1,
                      schemata="metadata",
                      default='',
                      widget=CalendarWidget(label='Date de Validation')),
        
        StringField('Valideurs',
                   searchable=1,
                   required=1,
                   isMetadata=1,
                   speedmeta=1,
                   schemata="metadata",
                   default='',
                   multiValued=1,
                   widget=StringWidget(label='Valideur(s)')),
                   
       ReferenceField('publishPlaces',
                   relationship = 'publishTo',
                   referenceClass = PublishPlacementReference,
                   multiValued = True,
                   isMetadata = True,
                   schemata="metadata",
                   languageIndependent = True,
                   index = 'KeywordIndex',
                   #write_permission = ModifyPortalContent,
                   allowed_types=('SpeedFolder',),
                   widget = ReferenceBrowserWidget(
                               allow_search = False,
                               allow_browse = True,
                               show_indexes = False,
                               force_close_on_insert = False,
                           label = "Emplacements de publication",
                           #label_msgid = "label_relae") and portal.portal_membership.checkPermission("Add portal content", object.aq_inner.getParentNode()) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)ted_items",
                           description = "Emplacements possibles de publication",
                           #description_msgid = "help_related_items",
                           #i18n_domain = "plone",
                           visible = {'edit' : 'visible', 'view' : 'invisible' }
                           )),
                           
       TextField('HTMLPreview',
                 default='',
                 searchable=1,
                 widget=TextAreaWidget(label='Previsualisation',
                                       visible ={'edit': 'invisible','view': 'invisible'}
                                       ),
                 default_output_type = 'text/html',
                 default_content_type = 'text/html',
            ),
), marshall=PrimaryFieldMarshaller()
)

SpeedFileSchema.addField(relatedItemsField.copy())
