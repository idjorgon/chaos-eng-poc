import boto3

def list_fis_experiments():
    fis_client = boto3.client('fis')
    
    try:
        response = fis_client.list_experiments()
        experiments = response.get('experiments', [])
        
        for experiment in experiments:
            print(f"Experiment ID: {experiment['id']}, State: {experiment['state']}, Tags: {experiment['tags']}")
    
    except Exception as e:
        print(f"Error listing experiments: {e}")

if __name__ == '__main__':
    list_fis_experiments()