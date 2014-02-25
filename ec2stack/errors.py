#!/usr/bin/env python
# encoding: utf-8

from ec2stack.core import Ec2stackError


def invalid_snapshot_id():
    raise Ec2stackError(
        '400',
        'InvalidSnapshot.NotFound',
        'The specified Snapshot Id does not exist.'
    )


def invalid_zone_id():
    raise Ec2stackError(
        '400',
        'InvalidZone.NotFound',
        'The specified Availability Zone Id does not exist.'
    )


def invalid_volume_id():
    raise Ec2stackError(
        '400',
        'InvalidVolume.NotFound',
        'The specified Volume Id does not exist.'
    )


def duplicate_keypair_name():
    raise Ec2stackError(
        '400',
        'InvalidKeyPair.Duplicate',
        'The keypair already exists.'
    )


def duplicate_security_group():
    raise Ec2stackError(
        '400',
        'InvalidGroup.Duplicate',
        'The security group already exists.'
    )


def invalid_security_group():
    raise Ec2stackError(
        '400',
        'InvalidGroup.NotFound',
        'The specified security group does not exist.'
    )


def invalid_permission():
    raise Ec2stackError(
        '400',
        'InvalidPermission.NotFound',
        'The specified permission does not exist in specified security group'
    )


def missing_paramater(parameter):
    raise Ec2stackError(
        '400',
        'MissingParameter',
        'The request must contain the parameter %s' % parameter
    )


def invalid_paramater_value(message):
    raise Ec2stackError(
        '400',
        'InvalidParameterValue',
        message
    )