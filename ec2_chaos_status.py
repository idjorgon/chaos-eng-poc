import boto3
import time
​
​
def main():
    # Initialize AWS clients
    fis_client = boto3.client('fis')
    ec2_client = boto3.client('ec2')
​
    # Initialize variables
    account_number = '537168545210'  # Replace with your AWS Account ID
    region = 'us-east-1'  # Replace with your AWS region
    role_arn = f"arn:aws:iam::{account_number}:role/service-role/AWSFISIAMRole-1693834158129"
    instance_id = 'i-0dca6993efd1fa24e'  # Replace with your EC2 instance ID
    resource_arn = f"arn:aws:ec2:{region}:{account_number}:instance/{instance_id}"
​
    # Check if EC2 instance is initially stopped
    ec2_response = ec2_client.describe_instance_status(InstanceIds=[instance_id])
    instance_status = ec2_response['InstanceStatuses'][0]['InstanceState']['Name'] \
        if ec2_response['InstanceStatuses'] else 'stopped'
​
    if instance_status == 'stopped':
        print("The EC2 instance is stopped. Starting it...")
        ec2_client.start_instances(InstanceIds=[instance_id])
        time.sleep(30)  # Waiting for EC2 instance to start
​
    # Create FIS experiment template
    create_response = fis_client.create_experiment_template(
        description='EC2 stop experiment',
        targets={
            'target1': {
                'resourceType': 'aws:ec2:instance',
                'resourceArns': [resource_arn],
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
                'value': f"arn:aws:cloudwatch:{region}:{account_number}:alarm:EC2-CPU-Alarm"
            }
        ],
        roleArn=role_arn
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
        ec2_response = ec2_client.describe_instance_status(InstanceIds=[instance_id])
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