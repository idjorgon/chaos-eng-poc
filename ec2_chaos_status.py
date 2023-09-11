import boto3
import time

# Initialize variables
ACCOUNT_NUMBER = "863615190391"
REGION = "us-east-2"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT_NUMBER}:role/my-fis-role"
INSTANCE_ID = "i-0dea9f7d20ea1bf93"
RESOURCE_ARN = f"arn:aws:ec2:{REGION}:{ACCOUNT_NUMBER}:instance/{INSTANCE_ID}"

def main():
    # Initialize AWS clients
    fis_client = boto3.client('fis')
    ec2_client = boto3.client('ec2')
    # Check if EC2 instance is initially stopped
    ec2_response = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
    instance_status = ec2_response['InstanceStatuses'][0]['InstanceState']['Name'] \
        if ec2_response['InstanceStatuses'] else 'stopped'
        
    if instance_status == 'stopped':
        print("The EC2 instance is stopped. Starting it...")
        ec2_client.start_instances(InstanceIds=[INSTANCE_ID])
        time.sleep(30)  # Waiting for EC2 instance to start
        
    # Create FIS experiment template
    create_response = fis_client.create_experiment_template(
        description='EC2 stop experiment',
        targets={
            'target1': {
                'resourceType': 'aws:ec2:instance',
                'resourceArns': [RESOURCE_ARN],
                'selectionMode': 'ALL'
            }
        },
        actions={
            'action1': {
                'actionId': 'aws:ec2:stop-instances',
                'targets': {'Instances': 'target1'}
            }
        },
        stopConditions=[
            {
                'source': 'aws:cloudwatch:alarm',
                'value': f"arn:aws:cloudwatch:{REGION}:{ACCOUNT_NUMBER}:alarm:EC2-CPU-Alarm"
            }
        ],
        roleArn=ROLE_ARN
    )
​
    template_id = create_response['experimentTemplate']['id']
    print(f"Experiment template created with ID: {template_id}")
​
    # Start FIS experiment
    start_response = fis_client.start_experiment(
        experimentTemplateId=template_id
    )
    experiment_id = start_response['experiment']['id']
    print(f"Experiment started with ID: {experiment_id}")
​
    # Monitoring
    while True:
        # You might want to add more logic here to check if the experiment is completed
        ec2_response = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
        instance_status = ec2_response['InstanceStatuses'][0]['InstanceState']['Name'] if ec2_response[
            'InstanceStatuses'] else 'stopped'
​
        print(f"EC2 Instance status: {instance_status}")
​
        if instance_status == 'stopped':
            print("EC2 instance is successfully stopped.")
            break
​
        time.sleep(10)  # Wait before checking the instance state again
​
​
if __name__ == '__main__':
    main()