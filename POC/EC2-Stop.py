import boto3
import time


def main():
    elb_client = boto3.client('elb', region_name='us-east-2')
    dns_name = 'tor-pe-qe-demo-app-be-clb-1-206864453.us-east-2.elb.amazonaws.com'

    # Get all classic load balancers
    response = elb_client.describe_load_balancers()

    # Filter the required load balancer using DNS name
    load_balancers = [lb for lb in response['LoadBalancerDescriptions'] if lb['DNSName'] == dns_name]

    if not load_balancers:
        print("Classic load balancer with the specified DNS name not found.")
        return

    lb = load_balancers[0]
    instance_ids = [instance['InstanceId'] for instance in lb['Instances']]

    print(instance_ids)

    # Select the second EC2 instance
    if len(instance_ids) < 2:
        print("There's only one EC2 instance or none associated with the classic load balancer. Exiting.")
        return

    INSTANCE_ID = instance_ids[1]
    print(f"Selected EC2 Instance ID: {INSTANCE_ID}")

    # Initialize Boto3 EC2 client
    ec2_client = boto3.client('ec2')

    # Fetch and print the public IP address
    ec2_response = ec2_client.describe_instances(InstanceIds=[INSTANCE_ID])
    instance_details = ec2_response['Reservations'][0]['Instances'][0]
    public_ip = instance_details.get('PublicIpAddress', None)

    if public_ip:
        print(f"Public IP Address of the EC2 instance {INSTANCE_ID}: {public_ip}")
    else:
        print(f"The EC2 instance {INSTANCE_ID} does not have a public IP address.")

    ACCOUNT_NUMBER = "863615190391"
    REGION = "us-east-2"
    ROLE_ARN = f"arn:aws:iam::{ACCOUNT_NUMBER}:role/my-fis-role"
    resource_arn = f"arn:aws:ec2:{REGION}:{ACCOUNT_NUMBER}:instance/{INSTANCE_ID}"

    fis_client = boto3.client('fis')

    # Check if EC2 instance is already stopped
    instance_state = instance_details['State']['Name']
    if instance_state == 'stopped':
        print("EC2 instance is stopped. Starting it.")
        ec2_client.start_instances(InstanceIds=[INSTANCE_ID])
        time.sleep(60)  # Wait for instance to start

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
                "source": "none"
            }
        ],
        roleArn=ROLE_ARN
    )

    template_id = create_response['experimentTemplate']['id']
    print(f"Experiment template created with ID: {template_id}")

    # Start FIS experiment
    start_response = fis_client.start_experiment(
        experimentTemplateId=template_id
    )
    experiment_id = start_response['experiment']['id']
    print(f"Experiment started with ID: {experiment_id}")

    # Monitoring
    while True:
        ec2_response = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
        instance_status = ec2_response['InstanceStatuses'][0]['InstanceState']['Name'] if ec2_response[
            'InstanceStatuses'] else 'stopped'

        print(f"EC2 Instance status: {instance_status}")

        if instance_status == 'stopped':
            print("EC2 instance is successfully stopped.")

            # Wait for 150 seconds
            print("Waiting for 150 seconds...")
            time.sleep(150)

            # Fetch a new EC2 instance.
            instance_id = get_instance_from_clb(dns_name)
            if instance_id:
                print(f"EC2 instance associated with the Classic Load Balancer {dns_name}: {instance_id}")
                print(f"get the ip address for {instance_id}")
                print(get_instance_public_ip(instance_id))

            break  # Break out of the loop once the above actions are done

        time.sleep(10)  # Wait before checking the instance state again


def get_instance_public_ip(instance_id):
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    # Fetch the details of the given EC2 instance
    response = ec2_client.describe_instances(InstanceIds=[instance_id])

    if response['Reservations'] and response['Reservations'][0]['Instances']:
        return response['Reservations'][0]['Instances'][0].get('PublicIpAddress', None)
    else:
        return None


def get_instance_from_clb(dns_name):
    elb_client = boto3.client('elb', region_name='us-east-2')

    # Get all classic load balancers
    response = elb_client.describe_load_balancers()

    # Filter the required load balancer using DNS name
    load_balancers = [lb for lb in response['LoadBalancerDescriptions'] if lb['DNSName'] == dns_name]

    if not load_balancers:
        print("Classic load balancer with the specified DNS name not found.")
        return None

    lb = load_balancers[0]
    instance_ids = [instance['InstanceId'] for instance in lb['Instances']]

    print(instance_ids)

    if instance_ids:
        # Return the last instance in the list
        return instance_ids[-1]
    else:
        print(f"No EC2 instances associated with the Classic Load Balancer: {dns_name}")
        return None


if __name__ == '__main__':
    main()
