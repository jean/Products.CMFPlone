from types import StringType, TupleType, ListType
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.Expression import Expression

import ConfigurationMethods

ONEFOUR=1
_registry={}
_methods=('addSiteProperties',
          'setupDefaultSlots',
          'installExternalEditor',
          'assignTitles',
          'addMemberdata',
          'modifyMembershipTool',
          'addNewActions',
          'modifySkins',
          'installPortalTools')

def registerConfiguration(versions, configuration):
    _versions=()
    if type(versions) is StringType:
        _versions=(versions,)
    elif type(versions) is ListType:
        _versions=tuple(version)
    else:
        _versions=versions

    for methodname in _methods:
        setattr(configuration, methodname, getattr(ConfigurationMethods, methodname))

    _registry[_versions]=configuration

def getConfiguration(version):
    for versions, config in _registry.items():
        if version in versions:
            return config

class OriginalConfiguration:
    def addTypeActions(self, portal):
        tt=getToolByName(portal, 'portal_types')
        tt['Event'].addAction( 'metadata'
                             , 'Metadata'
                             , 'metadata_edit_form'
                             , CMFCorePermissions.ModifyPortalContent
                             , 'object' ) 

    def _installExternalEditor(self, portal):
        types_tool=getToolByName(self, 'portal_types')
        methods=('PUT', 'manage_FTPget') #if a definition has these methods it shoudl work
        exclude=('Topic', 'Event', 'Folder')
        for ctype in types_tool.objectValues():
            if ctype.getId() not in exclude:
                ctype.addAction( 'external_edit'
                               , 'External Edit'
                               , 'external_edit'
                               , CMFCorePermissions.ModifyPortalContent
                               , 'object'
                               , 0 )

    def modifyActions(self, portal):
        dt=getToolByName(portal, 'portal_discussion')
        dt_actions=dt._cloneActions()
        for a in dt_actions:
            if a.id=='reply':
                a.visible=0
        dt._actions=dt_actions

        st=getToolByName(portal, 'portal_syndication')
        st_actions=st._cloneActions()
        for a in st_actions:
            if a.id=='syndication':
                a.visible=0
        st._actions=st_actions

        tt=getToolByName(portal, 'portal_types')
        folder_actions=tt['Folder']._cloneActions()
        for a in folder_actions:
            if a.id=='folderlisting':
                a.visible = 0
            if a.id=='edit':
                a.name='Properties'
        tt['Folder']._actions=folder_actions

        file_actions=tt['File']._cloneActions()
        tt['File']._actions=[action for action in file_actions if action.id!='download']
        self.addTypeActions(portal)

        for t in tt.objectValues():
            _actions=t._cloneActions()
            for a in _actions:
                if a.id=='metadata':
                    a.name='Properties'
            t._actions=_actions

        at=getToolByName(portal, 'portal_actions')
        at_actions=at._cloneActions()
        for a in at_actions:
            if a.id=='folderContents' and a.category=='object':
                a.visible=0
            if a.id=='folderContents' and a.category=='folder':
                a.title='Contents'
        at._actions=at_actions

        if hasattr(portal, 'portal_registration'):
            rt=getToolByName(portal, 'portal_registration')
            rt_actions=rt._cloneActions()
            joinexpr='python: test(not member and portal.portal_membership.checkPermission("Add portal member", portal), 1, 0)'
            for a in rt_actions:
                if a.id=='join':
                    a.condition=Expression(joinexpr)
            rt._actions=rt_actions

        pp=getToolByName(portal, 'portal_properties')
        pp_actions=pp._cloneActions()
        for a in pp_actions:
            if a.id=='configPortal':
                a.title='Plone Setup'
                a.action=Expression('string:${portal_url}/portal_form/reconfig_form')
        pp._actions=pp_actions

        ut=getToolByName(portal, 'portal_undo')
        ut.addAction( 'undo'
                    , name='Quick Undo'
                    , action='string:${object_url}/quick_undo'
                    , condition='member'
                    , permission=CMFCorePermissions.UndoChanges
                    , category='user'
                    , visible=0)

    def plonify_typeActions(self, portal):
        types_tool=getToolByName(portal, 'portal_types')
        for ptype in types_tool.objectValues():
            ptype_actions=ptype._cloneActions()
            for action in ptype_actions:
                exprtxt=getattr(action.action,'text', action.action)
                if exprtxt.startswith('string:') and \
                    action.id in ('edit', 'metadata'):
                    action.action=Expression(text='string:portal_form/'+exprtxt[len('string:'):])
            ptype._actions=tuple(ptype_actions)

        actions_tool=getToolByName(portal, 'portal_actions')
        actions=actions_tool._cloneActions()
        for action in actions:
                if action.id=='content_status_history':
                    action.action=Expression('string:${object_url}/portal_form/content_status_history')
        actions_tool._actions=tuple(actions)

        actions_tool=getToolByName(portal, 'portal_registration')
        actions=actions_tool._cloneActions()
        for action in actions:
                if action.id=='join':
                    action.action=Expression('string:${portal_url}/portal_form/join_form')
        actions_tool._actions=tuple(actions)

registerConfiguration(('1.1','1.2','1.3'), OriginalConfiguration)

class OneFourConfiguration(OriginalConfiguration):

    def addTypeActions(self, portal):
        tt=getToolByName(portal, 'portal_types')
        tt['Event'].addAction( 'metadata',
                               name='Metadata',
                               action='string:metadata_edit_form',
                               condition='',
                               permission=CMFCorePermissions.ModifyPortalContent,
                               category='object')

    def _installExternalEditor(self, portal):
        types_tool=getToolByName(self, 'portal_types')
        methods=('PUT', 'manage_FTPget') 
        exclude=('Topic', 'Event', 'Folder')
        for ctype in types_tool.objectValues():
            if ctype.getId() not in exclude:
                ctype.addAction( 'external_edit',
                                 name='External Edit',
                                 action='external_edit',
                                 condition='',
                                 permission=CMFCorePermissions.ModifyPortalContent,
                                 category='object',
                                 visible=0 )

    def plonify_typeActions(self, portal):
        types_tool=getToolByName(portal, 'portal_types')
        for ptype in types_tool.objectValues():
            ptype_actions=ptype._cloneActions()
            for action in ptype_actions:
                exprtxt=getattr(action.action,'text', action.action)
                if not exprtxt.startswith('string:') and \
                    action.id in ('edit', 'metadata'):
                    action.action=Expression(text='string:portal_form/'+exprtxt)
            ptype._actions=tuple(ptype_actions)

        actions_tool=getToolByName(portal, 'portal_actions')
        actions=actions_tool._cloneActions()
        for action in actions:
                if action.id=='content_status_history':
                    action.action=Expression('string:${object_url}/portal_form/content_status_history')
        actions_tool._actions=tuple(actions)

        actions_tool=getToolByName(portal, 'portal_registration')
        actions=actions_tool._cloneActions()
        for action in actions:
                if action.id=='join':
                    action.action=Expression('string:${portal_url}/portal_form/join_form')
        actions_tool._actions=tuple(actions)
registerConfiguration('1.4', OneFourConfiguration)



