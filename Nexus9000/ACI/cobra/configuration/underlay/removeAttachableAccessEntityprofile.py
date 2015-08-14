#!/usr/bin/env python

from cobra.model.infra import AttEntityP, RsDomP, ProvAcc, FuncP, AccPortGrp, RsAttEntP

from createMo import *

DEFAULT_ENABLE_INFRASTRUCTURE_VLAN = 'False'

DOMAINS_CHOICES = ['layer2', 'layer3', 'physical', 'vcenter']


def input_key_args(msg='\nPlease Specify the Entity Profile:'):
    print msg
    return input_raw_input("Profile Name", required=True)


def input_domain_name():
    return {'name': input_raw_input('Domain name', required=True),
            'type': input_options('Domain Type', '', DOMAINS_CHOICES, required=True)}


def input_optional_args():
    args = {}
    args['enable_infrastructure_vlan'] = input_raw_input('Enable Infrastructure VLAN', default=DEFAULT_ENABLE_INFRASTRUCTURE_VLAN)
    args['domain_profiles'] = read_add_mos_args(add_mos('Add a Domain Profile', input_domain_name))
    args['interface_policy_group'] = input_raw_input('Interface Policy Group', 'None')
    return args


def remove_attachable_access_entity_profile(infra, entity_profile, **args):
    """Remove an attached entity profile. This also provides the removal of a Virtual Machine Management (VMM) domain and the physical network infrastructure. """
    args = args['optional_args'] if 'optional_args' in args.keys() else args
    
    infra_attentityp = AttEntityP(infra, entity_profile)
    infra_attentityp.delete()  

class RemoveAttachableAccessEntityProfile(CreateMo):

    def __init__(self):
        self.description = 'Remove an attached entity profile. This also provides the removal of a Virtual Machine Management (VMM) domain and the physical network infrastructure.'
        self.entity_profile = None
        super(RemoveAttachableAccessEntityProfile, self).__init__()

    def set_cli_mode(self):
        super(RemoveAttachableAccessEntityProfile, self).set_cli_mode()
        self.parser_cli.add_argument('entity_profile', help='The attached entity profile name.')
        self.parser_cli.add_argument('-v', '--enable_infrastructure_vlan', action='store_const', const=True, default= DEFAULT_ENABLE_INFRASTRUCTURE_VLAN, help='The provider access function. This is defined when the hypervisor is using an encapsulation protocol, such as VxLAN/NVGRE, and provides the policies to impacting VxLAN/NvGRE packets from NVGRE.')
        self.parser_cli.add_argument('-d', '--domains', dest='domain_profiles', nargs=2, help=' relation to a physical or virtual domain. Users need to create this to provide association between physical infrastructure policies and the domains.')
        self.parser_cli.add_argument('-g', '--interface_policy_group', help='The attachable policy group acts as an override of the policies given at the AccBaseGrp for the ports associated with the Attachable Entity Profile.')

    def read_key_args(self):
        self.entity_profile = self.args.pop('entity_profile')

    def wizard_mode_input_args(self):
        self.args['entity_profile'] = input_key_args()
        if not self.delete:
            self.args['optional_args'] = input_optional_args()

    def run_cli_mode(self):
        super(RemoveAttachableAccessEntityProfile, self).run_cli_mode()
        if not self.delete:
            self.args['domain_profiles'] = [{'name': self.args['domain_profiles'][0],
                                             'type': self.args['domain_profiles'][1]}]

    def delete_mo(self):
        self.check_if_mo_exist('uni/infra/attentp-', self.entity_profile, AttEntityP, description='Attachable Access Entity Profile')
        super(RemoveAttachableAccessEntityProfile, self).delete_mo()

    def main_function(self):
        # Query a tenant
        self.look_up_mo('uni/infra', '')
        remove_attachable_access_entity_profile(self.mo, self.entity_profile, optional_args=self.optional_args)

if __name__ == '__main__':
    mo = RemoveAttachableAccessEntityProfile()
