import boto3

ACCOUNT_NUMBER = "863615190391"
REGION = "us-east-2"
INSTANCE_ID = "i-0dea9f7d20ea1bf93"

def create_cloudwatch_alarm():
    cloudwatch = boto3.client('cloudwatch', region_name=REGION)
    alarm_name = "EC2-CPU-Alarm"
    metric_name = "CPUUtilization"
    namespace = "AWS/EC2"
    statistic = "Average"
    comparison = "GreaterThanOrEqualToThreshold"
    threshold = 70.0
    period = 300
    evaluation_periods = 1
    datapoints_to_alarm = 1
    actions_enabled = True
    # ARN for SNS Topic (Replace with your own)
    alarm_actions = [f"arn:aws:sns:{REGION}:{ACCOUNT_NUMBER}:tor-pe-qe-ay-test-sns"]
    cloudwatch.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator=comparison,
        EvaluationPeriods=evaluation_periods,
        DatapointsToAlarm=datapoints_to_alarm,
        MetricName=metric_name,
        Namespace=namespace,
        Period=period,
        Statistic=statistic,
        Threshold=threshold,
        ActionsEnabled=actions_enabled,
        AlarmActions=alarm_actions,
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': INSTANCE_ID
            }
        ]
    )
    print(f"CloudWatch Alarm {alarm_name} created.")

if __name__ == '__main__':
    create_cloudwatch_alarm()