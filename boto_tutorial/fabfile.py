import sys

import boto3
import logging
from fabric import task
from botocore.exceptions import ClientError

# use loggers right from the start, rather than 'print'
logger = logging.getLogger(__name__)
# this will log boto output to std out
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

from dotenv import dotenv_values
config = dotenv_values(".env")
container_name = 'COMSM0072_boto_lab'

@task
def create(c):
    ec2 = boto3.resource('ec2',
                         region_name='us-east-1',
                         # pass content of config file as named args
                         **config
                         )

    instances = ec2.create_instances(

        ImageId='ami-02e136e904f3da870',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        Placement={
            'AvailabilityZone': 'us-east-1a',
        },

    )
    iid = instances[0].id

    # give the instance a tag name
    ec2.create_tags(
        Resources=[iid],
        Tags=[{'Key': 'Name', 'Value': container_name}]
    )

    logger.info(instances[0])

@task
def check(c):

    ec2 = boto3.resource('ec2',
                         region_name='us-east-1',
                         **config)

    instances = ec2.instances.all();

    for i in instances:
        print(i.id)
    
    inst_names = [tag['Value'] for i in instances for tag in i.tags if tag['Key'] == 'Name']
    status = {name : i.state["Name"] for name in inst_names for i in instances}

    print(f'Container: {container_name}, is {status[container_name]}')

@task
def stop(c):

    ec2 = boto3.resource('ec2',
                         region_name='us-east-1',
                         **config)

    ec2_client = boto3.client('ec2',
                         region_name='us-east-1',
                         **config)

    instances = ec2.instances.all()

    inst_names = [tag['Value'] for i in instances for tag in i.tags if tag['Key'] == 'Name']
    ids = {name : i.id for name in inst_names for i in instances}

    try:
        ec2_client.stop_instances(InstanceIds=[ids[container_name]], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    try:
        response = ec2_client.stop_instances(InstanceIds=[ids[container_name]], DryRun=False)
        print(response)
    except ClientError as e:
        print(e)
