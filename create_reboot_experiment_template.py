import boto3
from wait_for_new_instance import get_new_instance

def create_reboot_experiment_template():
    fis_client = boto3.client('fis')
    
    try:
        response = fis_client.create_experiment_template(
            description='Reboot EC2 Instance',
            stopConditions=[
                {
                    'source': 'none',
                },
            ],
            targets={
                'Instances-Target-1': {
                    'resourceType': 'aws:ec2:instance',
                    'resourceArns': [
                        'arn:aws:ec2:us-east-2:863615190391:instance/i-0992c2f9ea88bcbdb', # Replace/add new instance arn 
                    ],
                'selectionMode': 'ALL',
                }
            },
            actions={
                'Reboot': {
                    'actionId': 'aws:ec2:reboot-instances',
                    'description': 'Reboot EC2',
                    'parameters': {},
                    'targets': {
                        'Instances': 'Instances-Target-1'
                    },
                }
            },
            roleArn='arn:aws:iam::863615190391:role/my-fis-role',
            tags={
                'Initiative': 'TOR-PE-QE',
                'Name': 'RebootInstances'
            },
        )
        
        print(f"Experiment template ID: {response['experimentTemplate']['id']}")
    
    except Exception as e:
        print(f"Error creating experiment template: {e}")

if __name__ == '__main__':
    create_reboot_experiment_template()