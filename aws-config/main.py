#!/usr/bin/env python
import json
from constructs import Construct
from cdktf import App, TerraformStack
from boto3.session import Session
from imports.aws import (
    AwsProvider, IamRole,
    ConfigConfigurationRecorder,
    ConfigConfigurationRecorderRecordingGroup,
    ConfigDeliveryChannel,
    ConfigDeliveryChannelSnapshotDeliveryProperties,
    ConfigConfigurationRecorderStatus
)


class AWSConfig(TerraformStack):
    def __init__(self, scope: Construct, ns: str, profile_name):
        super().__init__(scope, ns)

        # const
        self.tags = { "project": "aws-waf-manager"}
        self.environment = "dev".lower()
        self.application = "application".lower()
        self.resource_prefix = f"{self.application}-{self.environment}"
        self.tag_name_prefix = f"{self.application}-{self.environment}-region"
        self.profile_name = profile_name


    def enable_aws_config(
        self,
        account_id,
        region,
        bucket_name,
        include_global_resources,
        create_role,
        iam_role_arn=None,
        topic_arn=None,
        frequency="Six_Hours"
    ):
        """
        Enables AWS config in provide account_id, region, partition
        """
        partition = "aws-us-gov" if "gov" in region else "aws"
        aws_provider = AwsProvider(self, f"aws-{region}", region=region, profile=self.profile_name, alias = f"aws-{region}")

        if create_role:
            iam_role_arn = self.create_iam_role(partition)
        # else:
        #     iam_role_arn = f"arn:{partition}:iam::{account_id}:role/{self.resource_prefix}-global-awsconfig-role"
        
        recorder = ConfigConfigurationRecorder(self,f"recorder-{region}",
            role_arn = iam_role_arn,
            recording_group = [
                ConfigConfigurationRecorderRecordingGroup(all_supported=True,
                    include_global_resource_types=include_global_resources
                )
            ],
            provider = aws_provider
        )
        delivery_channel = ConfigDeliveryChannel(self, f"delivery_channel-{region}",
            s3_bucket_name = bucket_name,
            snapshot_delivery_properties = [
                ConfigDeliveryChannelSnapshotDeliveryProperties(delivery_frequency=frequency)
            ],
            sns_topic_arn = topic_arn,
            depends_on = [recorder],
            provider = aws_provider
        )
        recorder_status = ConfigConfigurationRecorderStatus(self, f"recorder_status-{region}",
            is_enabled = True,
            name = recorder.name,
            depends_on = [delivery_channel],
            provider = aws_provider
        )

        

    def add_config_rule():
        """
        Add new config rule
        """
        pass

    def create_iam_role(self, partition):
        """
        Helper method to create IAM role for AWS Config
            * partition
        """
        region = "us-gov-west-1" if "gov" in partition else "us-east-1"
        aws_provider = AwsProvider(self, f"iam-aws-{region}", region=region, profile=self.profile_name)
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["config.amazonaws.com"]
                    },
                    "Action": ["sts:AssumeRole"]
                }
            ]
        }
        managed_policy_arn = f"arn:{partition}:iam::aws:policy/service-role/AWS_ConfigRole"

        aws_config_role = IamRole(self,"aws_config_role",
            name = f"{self.resource_prefix}-global-awsconfig-role",
            path = "/",
            assume_role_policy = json.dumps(assume_role_policy),
            managed_policy_arns = [managed_policy_arn],
        )
        return aws_config_role.arn

def get_available_regions(partition):
    """
    Helper method to get list of supported regions 
    based on provided partition.
    """
    sess = Session()
    aws_config_regions = sess.get_available_regions('config',partition_name=partition, allow_non_regional=False)
    return aws_config_regions

def enable_aws_config_in_account(account_id, profile_name, partition, default_regions):
    
    app = App(stack_traces=False)
    aws_config = AWSConfig(app, f"aws-config-{account_id}", profile_name)
    iam_role_arn = aws_config.create_iam_role(partition)
    # regions = get_available_regions(partition)
    regions = ["us-east-1", "us-east-2"]
    
    for region in regions:
        print(f"region = {region}")
        aws_config.enable_aws_config(
            account_id=account_id,
            region = region,
            bucket_name="devops-lambda-pipeline-artifacts",
            include_global_resources=True if region in default_regions else False,
            create_role = False,
            iam_role_arn=iam_role_arn,
        )
    app.synth()


def main():
    default_regions=["us-east-1",]
    account_list = {"9999": "dev", "8888": "prod"}
    for account, profile in account_list.items():
        enable_aws_config_in_account(account_id=account, profile_name=profile, partition="aws", default_regions=default_regions)


if __name__ == "__main__":
    main()