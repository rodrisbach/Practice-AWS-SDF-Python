import boto3
import json
from botocore.exceptions import ClientError

class SecurityGroup():

    def __init__(self,profile):
        self.vpcID = None
        self.profile = profile

    def get_vpc_ID(self):
        session = boto3.Session(profile_name=self.profile)
        ec2 = session.client('ec2')
        vpc = ec2.describe_vpcs()
        self.vpcID = vpc['Vpcs'][0]['VpcId']
        return self.vpcID

    def is_there_a_security_group(self, sg_name):
        session = boto3.Session(profile_name=self.profile)
        ec2 = session.client('ec2')
        response = ec2.describe_security_groups(
            Filters = [
                {
                    'Name': 'vpc-id',
                    'Values': [
                        self.vpcID
                    ],
                },
                {
                    'Name': 'tag:owner',
                    'Values': [
                        'rsbach'
                    ],
                },
            ],
            GroupNames = [
                sg_name
            ],
            DryRun = False
        )
        return response  

    def create_securityGroup(self, sg_name):
        session = boto3.Session(profile_name=self.profile)
        ec2 = session.client('ec2')
        security_group = ec2.create_security_group(
            Description = 'training-rschanzenbach',
            GroupName = sg_name,
            VpcId = self.vpcID
        )
        sgID = security_group['GroupId']
        ec2.create_tags(
            DryRun = False,
            Resources = [
                sgID,
            ],
            Tags = [
                {
                    'Key': 'environment',
                    'Value': 'training'
                },
                {
                    'Key': 'owner',
                    'Value': 'rsbach'
                },
            ]
        )
        return sgID

    def authorize_ingress_securityGroup(self,sgID):
        session = boto3.Session(profile_name=self.profile)
        ec2 = session.client('ec2')
        authorize_ingress_sg = ec2.authorize_security_group_ingress(
            GroupId = sgID,
            IpPermissions = [
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol':'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        return authorize_ingress_sg
    
    def delete_SecurityGroup(self,sgID):
        choice = input("Are you sure that you want to delete the Security Group that has been created before? \n(y/n)" )
        while choice != 'y' and choice != 'n':
            choice = str(input("Invalid option, try again (y/n)"))
        if choice == 'y' :
            session = boto3.Session(profile_name=self.profile)
            ec2 = session.client('ec2')
            securitygroup = ec2.delete_security_group(GroupId = sgID)
            print("The security group has been deleted")
            return securitygroup


class EC2_Instance():
    def __init__(self, ami, profile, instance_type, instance_name,user_data):
        self.ami = ami
        self.instance_type = instance_type
        self.profile = profile
        self.instance_name = instance_name
        self.user_data = user_data


    def create_instance(self, sgID, minCount, maxCount):
        session = boto3.Session(profile_name=self.profile)
        ec2 = session.client('ec2')

        instance = ec2.run_instances(
            ImageId = self.ami,
            InstanceType = self.instance_type,
            MaxCount = maxCount,
            MinCount = minCount,
            SecurityGroupIds=[
                sgID,
            ],
            KeyName = 'ansible-training-own-account',
            UserData = self.user_data,
            Monitoring = {
                'Enabled': False
            },
            TagSpecifications = [
                {'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': self.instance_name
                    },
                    {
                        'Key': 'environment',
                        'Value': 'training'
                    },
                    {
                        'Key': 'owner',
                        'Value': 'rsbach'
                    }
                    ]
                },
            ],
        )
        instances_list = []
        for i in range(minCount):
            instances_list.append(instance['Instances'][i]['InstanceId'])
        return instances_list

    def delete_instances(self, instances_list):
        choice = input("Are you sure that you want to delete the Instances that has been created before? \n(y/n)" )
        while choice != 'y' and choice != 'n':
            choice = str(input("Invalid option, try again (y/n)"))
        if choice == 'y' :
            session = boto3.Session(profile_name=self.profile)
            ec2 = session.client('ec2')
            try:
                ec2.terminate_instances(
                    InstanceIds = instances_list
                )
            except ClientError as e:
                print(e)


    def create_instance_list(self, instances_list, file_name):
        with open(file_name,"w") as file:
            for i in instances_list:
                file.write("%s\n" %i)

    def create_ansible_inventory(self, profile, file_path):
        session = boto3.Session(profile_name=self.profile)
        ec2 = session.client('ec2')
        inventory_group = "[ec2-testing]"
        instances_list = []
        with open(file_path,"r") as file:
            filecontents = file.readlines()
        for line in filecontents:
            current_instance = line[:-1]
            instances_list.append(current_instance)
        print(instances_list)
        IP_instances = []
        for i in instances_list:
            instances = ec2.describe_instances(
                Filters = [
                    {
                        'Name':'tag:owner',
                        'Values': [
                            'rsbach'
                        ],
                    },
                ],
                InstanceIds = [
                   i,
                ],
            )
            IP_instances.append(instances['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['Association']['PublicIp'])
        with open("inventory","w") as file:
            file.write("%s\n"%inventory_group)
            for i in IP_instances:
                file.write("%s\n" %i) 