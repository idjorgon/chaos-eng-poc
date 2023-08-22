import boto3
import pytest

def test_list_fis_experiments():
    fis_client = boto3.client('fis')
    
    try:
        response = fis_client.list_experiments()
        experiments = response.get('experiments', [])

        # Assert that experiments is a list
        assert isinstance(experiments, list)

        for experiment in experiments:
            # Assert that each experiment has an 'id' key
            assert 'id' in experiment
            # Assert that each experiment has a 'state' key
            assert 'state' in experiment
    
    except Exception as e:
        pytest.fail(f"Error listing experiments: {e}")

if __name__ == '__main__':
    pytest.main()