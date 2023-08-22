import boto3

def list_fis_experiment_templates():
    fis_client = boto3.client('fis')
    
    try:
        response = fis_client.list_experiment_templates()
        templates = response.get('experimentTemplates', [])
        
        for template in templates:
            print(f"Template ID: {template['id']}")
    
    except Exception as e:
        print(f"Error listing experiment templates: {e}")

if __name__ == '__main__':
    list_fis_experiment_templates()