import boto3
import pytest

@pytest.fixture(scope="module")
def ec2_client():
    # Initialize the EC2 client
    ec2 = boto3.client('ec2')
    return ec2

def test_list_ec2_instances(ec2_client):
    try:
        # Use describe_instances to list EC2 instances
        response = ec2_client.describe_instances()
        reservations = response.get('Reservations', [])
        
        # Assert that reservations is a list
        assert isinstance(reservations, list)
        
        for reservation in reservations:
            instances = reservation.get('Instances', [])
            for instance in instances:
                # Assert that each instance has the following keys
                assert 'InstanceId' in instance
                assert 'State' in instance
                assert 'InstanceType' in instance
                assert 'ImageId' in instance
                assert 'SubnetId' in instance
                assert 'VpcId' in instance
    
    except Exception as e:
        pytest.fail(f"Error listing EC2 instances: {e}")

if __name__ == '__main__':
    pytest.main()
