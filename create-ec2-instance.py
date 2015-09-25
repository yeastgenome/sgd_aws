#!/usr/local/bin/python

from boto.ec2.blockdevicemapping import (
    BlockDeviceMapping,
    BlockDeviceType,
)
import argparse
import boto.ec2
import sys
import time

def main():

    parser = argparse.ArgumentParser(description="Deploy AWS instance",)
    parser.add_argument('--service_name', help="service: jbrowse or jbrowse-dev")
    parser.add_argument('--availability_zone', default=None, help="region availability zone")
    parser.add_argument('instance_name')
    parser.add_argument('aws_profile')

    args = parser.parse_args()
    print args

    conn = boto.ec2.connect_to_region("us-west-2", profile_name=str.lower(args.aws_profile))
    
    if str.lower(args.service_name) == 'jbrowse':
        cloud_config_file = '/Users/kkarra/Dev/sgd_aws/cloud-config-jbrowse.yaml'
        root_vol_size = 30
        data_vol_size = 0
        key_name = 'jbrowse'
        ami_id = 'ami-5189a661'
        instance_type = 'm3.medium'
        instance_profile_arn = None
    elif str.lower(args.service_name) == 'jbrowse-dev':
        cloud_config_file = '/Users/kkarra/Dev/sgd_aws/cloud-config-jbrowse-dev.yaml'
        root_vol_size = 16
        data_vol_size = 200
        key_name = 'jbrowse-dev'
        instance_type = 'm3.medium'
        ami_id = 'ami-5189a661'
        instance_profile_arn = None
    else:
        sys.exit("Error: invalid service name")

    bdm = BlockDeviceMapping()
    bdm['/dev/sda1'] = BlockDeviceType(volume_type='gp2', delete_on_termination=True, size=root_vol_size)
    eph0 = BlockDeviceType()
    eph0.ephemeral_name = 'ephemeral0'
    bdm['/dev/sdb'] = eph0

    if data_vol_size:
        bdm['/dev/sdc'] = BlockDeviceType(volume_type='gp2', delete_on_termination=True, size=data_vol_size)

    with open(cloud_config_file, "r") as config_file:
        user_data = config_file.read()
    print user_data

    reservation = conn.run_instances(
        image_id=ami_id,
        instance_type=instance_type,
        security_groups=['sgd-jbrowse'],
        placement=args.availability_zone,
        user_data=user_data,
        block_device_map=bdm,
        instance_initiated_shutdown_behavior='terminate',
        instance_profile_arn=instance_profile_arn,
        key_name=key_name)
    
    time.sleep(0.5)  # sleep for a moment to ensure instance exists...
    instance = reservation.instances[0]
    instance.add_tags({
        'Name': args.instance_name,
    })


if __name__ == '__main__':
    main()
