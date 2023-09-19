import boto3
import time


def create_fis_experiment_template():
    fis = boto3.client('fis')

    template_params = {
        "description": "Reboot-RDS",
        "targets": {
            "Clusters-Target-1": {
                "resourceType": "aws:rds:db",
                "resourceArns": [
                    "arn:aws:rds:us-east-2:863615190391:db:demobedb"
                ],
                "selectionMode": "ALL"
            }
        },
        "actions": {
            "stop": {
                "actionId": "aws:rds:reboot-db-instances",
                "parameters": {},
                "targets": {
                    "DBInstances": "Clusters-Target-1"
                }
            }
        },
        "stopConditions": [
            {
                "source": "none"
            }
        ],
        "roleArn": "arn:aws:iam::863615190391:role/service-role/AWSFISIAMRole-QE",
        "logConfiguration": {
            "s3Configuration": {
                "bucketName": "rds-logs-saad"
            },
            "logSchemaVersion": 2
        }
    }

    try:
        response = fis.create_experiment_template(
            description=template_params["description"],
            targets=template_params["targets"],
            actions=template_params["actions"],
            stopConditions=template_params["stopConditions"],
            roleArn=template_params["roleArn"],
            logConfiguration=template_params["logConfiguration"]
        )
        print("Experiment template created successfully!")
        return response['experimentTemplate']['id']
    except Exception as e:
        print(f"Error creating experiment template. Reason: {e}")
        return None


def start_fis_experiment(template_id):
    fis = boto3.client('fis')
    try:
        response = fis.start_experiment(
            experimentTemplateId=template_id
        )
        print(f"Experiment started! Experiment ID: {response['experiment']['id']}")
    except Exception as e:
        print(f"Error starting experiment. Reason: {e}")


def check_rds_status(instance_arn):
    rds = boto3.client('rds')
    try:
        response = rds.describe_db_instances(
            DBInstanceIdentifier=instance_arn.split(":")[-1]
        )
        status = response['DBInstances'][0]['DBInstanceStatus']
        return status
    except Exception as e:
        print(f"Error retrieving RDS instance status. Reason: {e}")
        return None


# Main Execution
if __name__ == "__main__":
    # 1. Check status before starting the experiment
    initial_status = check_rds_status("arn:aws:rds:us-east-2:863615190391:db:demobedb")
    print(f"Initial RDS Instance Status: {initial_status}")

    if initial_status == "available":
        template_id = create_fis_experiment_template()
        if template_id:
            start_fis_experiment(template_id)

            time.sleep(5)  # Allow some time for the experiment to affect the RDS instance

            # 2. Wait for the status to change to "rebooting"
            while True:
                current_status = check_rds_status("arn:aws:rds:us-east-2:863615190391:db:demobedb")
                if current_status == "rebooting":
                    print(f"RDS Instance Status: {current_status}")
                    break
                time.sleep(5)

            # 3. Wait for the status to change back to "available"
            while True:
                current_status = check_rds_status("arn:aws:rds:us-east-2:863615190391:db:demobedb")
                if current_status == "available":
                    print(f"RDS Instance Status: {current_status}")
                    break
                time.sleep(5)
