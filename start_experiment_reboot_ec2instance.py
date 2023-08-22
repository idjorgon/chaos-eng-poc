import boto3

def start_fis_experiment(experiment_template_id):
    fis_client = boto3.client('fis', region_name='us-east-2')

    tags = {
        'Initiative': 'TOR-PE-QE',
        'Name': 'RebootEC2Instance'
    }

    try:
        response = fis_client.start_experiment(
            experimentTemplateId=experiment_template_id,
            tags=tags
        )

        experiment_id = response['experiment']['id']
        print(f"Experiment ID: {experiment_id}")
    
    except Exception as e:
        print(f"Error starting experiment: {e}")

if __name__ == '__main__':
    experiment_template_id = 'EnterExperimentTemplateID'
    start_fis_experiment(experiment_template_id)