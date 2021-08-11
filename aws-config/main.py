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
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # const
        self.tags = { "project": "aws-waf-manager"}
        self.environment = "dev".lower()
        self.application = "application".lower()
        self.resource_prefix = f"{self.application}-{self.environment}"
        self.tag_name_prefix = f"{self.application}-{self.environment}-region"


    def enable_aws_config(
        self,
        account_id,
        region,
        bucket_name,
        include_global_resources,
        create_role,
        # iam_role_arn,
        topic_arn=None,
        frequency="6h"
    ):
        """
        Enables AWS config in provide account_id, region, partition
        """
        partition = "aws-us-gov" if "gov" in region else "aws"
        aws_provider = AwsProvider(self, 'Aws', region=region)
        if create_role:
            iam_role_arn = self.create_iam_role(partition)
        else:
            iam_role_arn = f"arn:{partition}:iam::{account_id}:role/{self.resource_prefix}-global-awsconfig-role"
        recorder = ConfigConfigurationRecorder(self,"recorder",
            role_arn = iam_role_arn,
            recording_group = [
                ConfigConfigurationRecorderRecordingGroup(all_supported=True,
                    include_global_resource_types=include_global_resources
                )
            ]
        )
        delivery_channel = ConfigDeliveryChannel(self, "delivery_channel",
            s3_bucket_name = bucket_name,
            snapshot_delivery_properties = [
                ConfigDeliveryChannelSnapshotDeliveryProperties(delivery_frequency=frequency)
            ],
            sns_topic_arn = topic_arn,
            depends_on = [recorder]
        )
        recorder_status = ConfigConfigurationRecorderStatus(self, "recorder_status",
            is_enabled = True,
            name = recorder.name,
            depends_on = [delivery_channel]
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
        # aws_provider = AwsProvider(self, 'Aws')
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

def enable_aws_config_in_account(account_id, partition, default_regions):

    for region in get_available_regions(partition):
        print(f"region = {region}")
        app = App(stack_traces=False)
        aws_config = AWSConfig(app, f"aws-config-{account_id}-{region}")
        aws_config.enable_aws_config(
            account_id="9999",
            region = region,
            bucket_name="test-bucket",
            include_global_resources=True if region in default_regions else False,
            create_role=True if region in default_regions else False,
        )
        app.synth()


def main():
    enable_aws_config_in_account(account_id="9999", partition="aws-us-gov", default_regions=["us-east-1", "us-gov-west-1"])


if __name__ == "__main__":
    main()