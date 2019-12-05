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
NEWUSER="rsbach"
NEWUSERKEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCxnVAjZ1T4mkQlzcz+ureqhan8/r/Ti0fsqtThMmMBMfdfTVZ4Yy6c+ji0vc5yCfm52cN3vScL5Ok5yusUGrd9fNOb/LqFS1OUvYWhe5LXw1/7DF/60+yrW9dnjY/jd1CtD72E8SZHtJqFa5wDMNh/9CDZIPdheLIIao/g6gDyYPV2ZELLIXE9pog62RopK9oAkHS4eyezvFMB0pqAn5GEHkJ8IPcJL8ZY5C4HG/Ar4h9+Fzu1cDOWr0ABAvj07z0zaXUgJmnFNdO24+8Kye/NXEW+NTH2iVDweLlEmjNEP+4UPx1mVB6Glivwulqc1z7ctKp6eIwojUZk83FDbY1L rsbach@edrans-pc"
adduser $NEWUSER
echo "$NEWUSER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
mkdir /home/$NEWUSER/.ssh
echo $NEWUSERKEY >> /home/$NEWUSER/.ssh/authorized_keys
chown -R $NEWUSER:$NEWUSER /home/$NEWUSER/.ssh
chmod 0700 /home/$NEWUSER/.ssh
chmod 0600 /home/$NEWUSER/.ssh/authorized_keys"""

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