#!/usr/bin/env python
# encoding: utf-8

from flask import request

from ec2stack import helpers
from ec2stack.core import Ec2stackError
from ec2stack.providers.cloudstack import requester


@helpers.authentication_required
def create_security_group():
    helpers.require_parameters(['GroupName', 'GroupDescription'])
    response = _create_security_group_request()
    return _create_security_group_response(response)


def _create_security_group_request():
    args = {}
    args['command'] = 'createSecurityGroup'
    args['name'] = helpers.get('GroupName', request.form)
    args['description'] = helpers.get('GroupDescription', request.form)

    response = requester.make_request(args)

    response = response['createsecuritygroupresponse']

    return response


def _create_security_group_response(response):
    if 'errortext' in response:
        name = helpers.get('GroupName', request.form)
        raise Ec2stackError(
            '400',
            'InvalidGroupName.Duplicate',
            'The groupname \'%s\' already exists.' % name
        )
    else:
        response = response['securitygroup']
        return {
            'template_name_or_list': 'create_security_group.xml',
            'response_type': 'CreateSecurityGroupResponse',
            'id': response['id'],
            'return': 'true'
        }


@helpers.authentication_required
def delete_security_group():
    response = _delete_security_group_request()
    return _delete_security_group_response(response)


def _delete_security_group_request():
    args = {}

    helpers.require_one_paramater(['GroupName', 'GroupId'])

    if helpers.contains_parameter('GroupName'):
        args['name'] = helpers.get('GroupName', request.form)

    elif helpers.contains_parameter('GroupId'):
        args['id'] = helpers.get('GroupId', request.form)

    args['command'] = 'deleteSecurityGroup'

    response = requester.make_request(args)

    return response


def _delete_security_group_response(response):
    return {
        'template_name_or_list': 'status.xml',
        'response_type': 'DeleteSecurityGroupResponse',
        'return': 'true'
    }


@helpers.authentication_required
def authenticate_security_group_ingress():
    response = _authenticate_security_group_request('ingress')
    return _authenticate_security_group_response(response)


@helpers.authentication_required
def authenticate_security_group_egress():
    response = _authenticate_security_group_request('egress')
    return _authenticate_security_group_response(response)


def _authenticate_security_group_request(type):
    args = {}
    args = _parse_security_group_request()

    if type == 'egress':
        args['command'] = 'authorizeSecurityGroupEgress'
    elif type == 'ingress':
        args['command'] = 'authorizeSecurityGroupIngress'

    response = requester.make_request_async(args)

    return response


def _authenticate_security_group_response(response):
    if 'errortext' in response:
        if 'Failed to authorize security group' in response['errortext']:
            cidrlist = str(helpers.get('CidrIp', request.form))
            protocol = str(helpers.get('IpProtocol', request.form))
            fromPort = str(helpers.get('FromPort', request.form))
            toPort = str(helpers.get('toPort', request.form))
            raise Ec2stackError(
                '400',
                'InvalidPermission.Duplicate',
                'the specified rule "peer: ' + cidrlist + ', ' + protocol +
                ', from port: ' + fromPort + ', to port: ' + toPort +
                ', ALLOW" already exists'
            )
        elif 'Unable to find security group' in response['errortext']:
            raise Ec2stackError(
                '400',
                'InvalidGroup.NotFound',
                'Unable to find group \'%s\''
            )
        raise Ec2stackError(
            '400',
            'InvalidParameterValue',
            response['errortext']
        )
    else:
        return {
            'template_name_or_list': 'status.xml',
            'response_type': 'AuthorizeSecurityGroupIngressResponse',
            'return': 'true'
        }


@helpers.authentication_required
def revoke_security_group_ingress():
    response = _revoke_security_group_request('ingress')
    return _authenticate_security_group_response(response)


@helpers.authentication_required
def revoke_security_group_egress():
    response = _revoke_security_group_request('egress')
    return _authenticate_security_group_response(response)


def _revoke_security_group_request(type):
    args = {}

    rules = _parse_security_group_request()

    if type == 'ingress':
        args['command'] = 'revokeSecurityGroupIngress'
        args['id'] = _find_rule(rules, 'ingressrule')
    elif type == 'egress':
        args['command'] = 'revokeSecurityGroupEgress'
        args['id'] = _find_rule(rules, 'egressrule')

    response = requester.make_request_async(args)

    return response


def _revoke_security_group_response(response):
    if 'errortext' in response:
        raise Ec2stackError(
            '400',
            'InvalidParameterValue',
            response['errortext']
        )
    else:
        return {
            'template_name_or_list': 'status.xml',
            'response_type': 'AuthorizeSecurityGroupIngressResponse',
            'return': 'true'
        }


def _find_rule(rule, rule_type):
    security_group = _get_security_group(rule)

    found_rules = security_group[rule_type]

    for found_rule in found_rules:
        if _compare_rules(rule, found_rule):
            return found_rule['ruleid']

    raise Ec2stackError(
        '400',
        'InvalidPermission.NotFound',
        'The specified rule does not exist in this security group'
    )


def _compare_rules(left, right):
    protocol_match = str(left['protocol']) == str(right['protocol'])
    cidr_match = str(left['cidrlist']) == str(right['cidr'])

    if 'startport' in left and 'startport' in right:
        startPort_match = str(left['startport']) == str(right['startport'])
    elif 'icmptype' in left and 'icmptype' in right:
        startPort_match = str(left['icmptype']) == str(right['icmptype'])
    else:
        startPort_match = False

    if 'endport' in left and 'endport' in right:
        endPort_match = str(left['endport']) == str(right['endport'])
    elif 'icmpcode' in left and 'icmpcode' in right:
        endPort_match = str(left['icmpcode']) == str(right['icmpcode'])
    else:
        endPort_match = False

    return protocol_match and cidr_match and startPort_match and endPort_match


def _get_security_group(rule):
    response = _describe_security_groups_request(rule)

    if 'count' in response:
        for security_group in response['securitygroup']:
            if 'securityGroupId' in rule and security_group['id'] == rule[
                'securityGroupId']:
                return security_group
            elif 'securityGroupName' in rule and security_group['name'] == rule[
                'securityGroupName']:
                return security_group

    raise Ec2stackError(
        '400',
        'InvalidGroup.NotFound',
        'Unable to find group'
    )


def _describe_security_groups_request(args=None):
    if args is None:
        args = {}

    args['command'] = 'listSecurityGroups'

    response = requester.make_request(args)
    response = response['listsecuritygroupsresponse']

    return response


def _parse_security_group_request(args=None):
    if args is None:
        args = {}

    helpers.require_one_paramater(['GroupName', 'GroupId'])

    if helpers.contains_parameter('GroupName'):
        args['securityGroupName'] = helpers.get('GroupName', request.form)
    elif helpers.contains_parameter('GroupId'):
        args['securityGroupId'] = helpers.get('GroupId', request.form)

    if _contains_key_with_keyword('IpPermissions'):
        raise Ec2stackError(
            '400',
            'InvalidParameterCombination',
            'The parameter \'ipPermissions\' may not'
            'be used in combination with \'ipProtocol\''
        )
    else:
        helpers.require_parameters(['IpProtocol'])

        args['protocol'] = helpers.get('IpProtocol', request.form)

        helpers.require_parameters(['FromPort', 'ToPort', 'CidrIp'])

        if args['protocol'] in ['icmp']:
            args['icmptype'] = helpers.get('FromPort', request.form)
            args['icmpcode'] = helpers.get('ToPort', request.form)
        else:
            args['startport'] = helpers.get('FromPort', request.form)
            args['endport'] = helpers.get('ToPort', request.form)

        if helpers.get('CidrIp', request.form) is None:
            args['cidrlist'] = '0.0.0.0/0'
        else:
            args['cidrlist'] = helpers.get('CidrIp', request.form)

        return args


def _contains_key_with_keyword(keyword):
    return len([x for x in request.form if keyword in x]) >= 1
