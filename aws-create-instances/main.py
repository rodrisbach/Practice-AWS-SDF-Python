#!/usr/bin/python3

from instances_and_sgroup import SecurityGroup
from instances_and_sgroup import EC2_Instance
from botocore.exceptions import ClientError
ami = 'ami-0c322300a1dd5dc79'
sg_name = 'ansible-training'
profile_name = 'ansible-training'
instance_type = 't2.micro'
instance_name = 'ansible-training'
user_data = """#!/bin/bash
ls """
new_sg = SecurityGroup(profile_name)
new_sg.get_vpc_ID()
try:
    response = new_sg.is_there_a_security_group(sg_name)
    print("The security groups already exists")
    security_groupID = response['SecurityGroups'][0]['GroupId']

except ClientError as e:
    security_groupID = new_sg.create_securityGroup(sg_name)
    new_sg.authorize_ingress_securityGroup(security_groupID)

finally:
    print(f"Security Group Name: {sg_name} \nSecurity Group ID: {security_groupID}")

new_sg.delete_SecurityGroup(security_groupID)

new_instance = EC2_Instance(ami,profile_name,instance_type,instance_name,user_data)
instance_list = new_instance.create_instance(security_groupID,2,2)
new_instance.create_instance_list(instance_list)
new_instance.create_ansible_inventory(profile_name,"instance_list.txt")
new_instance.delete_instances(instance_list)
