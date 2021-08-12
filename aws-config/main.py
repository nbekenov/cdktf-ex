#!/usr/bin/env python
"""
AWS Config CDK-TF module
"""
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
    """
    AWS Config class
    available public methods:
        * enable_awsconfig_in_region
        * enable_awsconfig_in_account
        * add_config_rule - TBD
    """
    def __init__(self, scope: Construct, ns: str, profile_name, partition):
        super().__init__(scope, ns)

        # const
        self.tags = { "project": "aws-waf-manager"}
        self.environment = "dev".lower()
        self.application = "application".lower()
        self.resource_prefix = f"{self.application}-{self.environment}"
        self.tag_name_prefix = f"{self.application}-{self.environment}-region"
        self.profile_name = profile_name
        self.partition = partition


    def enable_awsconfig_in_region(
        self,
        region,
        bucket_name,
        include_global_resources,
        create_role=True,
        iam_role_arn=None,
        topic_arn=None,
        frequency="Six_Hours"
    ):
        """
        Enables AWS config in specified region for a particular account
        """
        aws_provider = AwsProvider(self, f"aws-{region}", region=region, profile=self.profile_name, alias = f"aws-{region}")
        if create_role:
            iam_role_arn = self.__create_iam_role()
        print(f"enabling AWS Config for region = {region} ...")

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

    def enable_awsconfig_in_account(self, account_id, bucket_name):
        """
        Enables AWS config in all supported regions
        """
        # This ensures that you don’t get redundant copies of IAM configuration Items in every Region.
        record_global_resources_region = "us-gov-west-1" if "gov" in self.partition else "us-east-1"
        iam_role_arn = self.__create_iam_role()

        for region in self.get_available_regions():
            self.enable_awsconfig_in_region(
                region = region,
                bucket_name=bucket_name,
                include_global_resources=region in record_global_resources_region,
                create_role = False,
                iam_role_arn=iam_role_arn,
            )
        print(f"AWS Config is enabled in all supported regions for account_id {account_id} in partition {self.partition}")

    def __create_iam_role(self):
        """
        Private helper method to create IAM role for AWS Config
        """
        # use default region for provider since IAM is a global resource
        region = "us-gov-west-1" if "gov" in self.partition else "us-east-1"
        AwsProvider(self, f"iam-aws-{region}", region=region, profile=self.profile_name)
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
        managed_policy_arn = f"arn:{self.partition}:iam::aws:policy/service-role/AWS_ConfigRole"

        aws_config_role = IamRole(self,"aws_config_role",
            name = f"{self.resource_prefix}-global-awsconfig-role",
            path = "/",
            assume_role_policy = json.dumps(assume_role_policy),
            managed_policy_arns = [managed_policy_arn],
        )
        print(f"IAM role for AWS Config was creted in region = {region} ")
        return aws_config_role.arn

    def get_available_regions(self):
        """
        Helper method to get list of supported regions
        based on provided partition.
        """
        sess = Session()
        aws_config_regions = sess.get_available_regions('config',partition_name=self.partition, allow_non_regional=False)
        return aws_config_regions


def main():
    """
    Enable AWS Config in all account from the list
    accounts_list = {
        "account_id": "profile_name"
    }
    """
    accounts_list = {"99999": "mydev", "88888": "myprod"}
    s3_bucket_name = "my-config-bucket"
    partition_name = "aws"

    for account, profile in accounts_list.items():
        app = App(stack_traces=False)
        aws_config = AWSConfig(app, f"aws-config-{account}", profile_name=profile, partition=partition_name)
        aws_config.enable_awsconfig_in_account(account_id=account, bucket_name=s3_bucket_name)
        app.synth()


if __name__ == "__main__":
    main()
