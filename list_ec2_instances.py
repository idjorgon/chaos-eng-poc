import boto3

# Initialize the EC2 client
ec2 = boto3.client('ec2')

# Use the describe_instances() method to get a list of EC2 instances
response = ec2.describe_instances()

# Loop through the reservations to extract instances
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        instance_state = instance['State']['Name']
        instance_type = instance['InstanceType']
        
        # Check if 'Name' tag exists in instance tags
        instance_name = ''
        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Name':
                instance_name = tag['Value']
                
        print(f"Instance ID: {instance_id}, Name: {instance_name}, State: {instance_state}, Type: {instance_type}")