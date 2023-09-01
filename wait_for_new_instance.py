# WIP: Not Tested
import boto3
import time

# region_name=us-east-2
def get_new_instance(region_name):
    # Initialize the EC2 client
    ec2 = boto3.client('ec2', region_name=region_name)

    # Wait for the new instance to become available
    while True:
        response = ec2.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    return instance  # Return the new instance once it's available
        time.sleep(10)  # Wait for 10 seconds before checking again