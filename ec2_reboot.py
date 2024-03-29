import boto3
import time

ACCOUNT_NUMBER = "863615190391"
REGION = "us-east-2"
INSTANCE_ID = "i-0dea9f7d20ea1bf93"
ROLE_ARN = f"arn:aws:iam::{ACCOUNT_NUMBER}:role/my-fis-role"

def main():
    # Initialize Boto3 clients
    ec2_client = boto3.client('ec2', region_name=REGION)
    fis_client = boto3.client('fis', region_name=REGION)

    # Check if EC2 instance is already stopped
    ec2_response = ec2_client.describe_instances(InstanceIds=[INSTANCE_ID])
    instance_state = ec2_response['Reservations'][0]['Instances'][0]['State']['Name']

    if instance_state == 'stopped':
        print("EC2 instance is stopped. Starting it.")
        ec2_client.start_instances(InstanceIds=[INSTANCE_ID])
        time.sleep(60)  # Wait for instance to start

    # Create FIS experiment template for rebooting EC2 instance
    response = fis_client.create_experiment_template(
        description="Reboot EC2 instance",
        targets={
            "Instances-Target-1": {
                "resourceType": "aws:ec2:instance",
                "resourceArns": [
                    f"arn:aws:ec2:{REGION}:{ACCOUNT_NUMBER}:instance/{INSTANCE_ID}"
                ],
                "selectionMode": "ALL"
            }
        },
        actions={
            "action1": {
                "actionId": "aws:ec2:reboot-instances",
                "targets": {
                    "Instances": "Instances-Target-1"
                }
            }
        },
        stopConditions=[
            {
                "source": "aws:cloudwatch:alarm",
                "value": "arn:aws:cloudwatch:us-east-2:863615190391:alarm:EC2-CPU-Alarm"
            }
        ],
        roleArn=ROLE_ARN
    )
    template_id = response['experimentTemplate']['id']
    print(f"Experiment template created with ID: {template_id}")

    # Start the experiment
    experiment = fis_client.start_experiment(experimentTemplateId=template_id)
    experiment_id = experiment['experiment']['id']
    print(f"Experiment started with ID: {experiment_id}")

    rebooted = False  # Flag to indicate whether the instance was rebooted

    # Monitor the EC2 instance
    while True:
        ec2_response = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
        instance_status = ec2_response['InstanceStatuses'][0]['InstanceState']['Name'] if ec2_response['InstanceStatuses'] else 'stopped'

        print(f"EC2 Instance status: {instance_status}")

        if instance_status == 'running' and rebooted:
            print("EC2 instance has been rebooted and is now running.")
            break
        elif instance_status == 'stopped':
            print("EC2 instance is stopped, which is unexpected. You might want to investigate.")
            break

        if instance_status == 'running' and not rebooted:
            rebooted = True  # Set the flag to True once the instance is initially running

        time.sleep(10)  # Wait before checking the instance state again

if __name__ == "__main__":
    main()