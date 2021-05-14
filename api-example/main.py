"""
sample stack of resources defined with CDK-TF
"""

import os
import sys
import json
import yaml
from cdktf import App, TerraformStack, TerraformOutput
from constructs import Construct
from imports.aws import (
    AwsProvider,
    ApiGatewayRestApi,
    ApiGatewayRestApiEndpointConfiguration,
    ApiGatewayDeployment,
    ApiGatewayStage,
    ApiGatewayMethodSettings,
    ApiGatewayMethodSettingsSettings,
)


# constants
tf_bucket_name = os.environ["TF_STATE_BUCKET_NAME"]

class CreateRestApi():
    pass

class MyApiStack(TerraformStack):
    """
    sample stack of resources defined with CDK-TF
    """

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        tags = {"ManagedBy": "terraform CDK", "user": "good.gentleman"}

        
        spec_yaml = "openapi-test.yaml"
        with open(spec_yaml, 'r') as file:
            data = yaml.load(file)
            open_api_body = yaml.dump(data)

        AwsProvider(self, "Aws", region="us-east-1")

        # aws_api_gateway_rest_api
        rest_api = ApiGatewayRestApi(
            self,
            "my_api",
            name="paymentconfig-api-test",
            endpoint_configuration=[
                ApiGatewayRestApiEndpointConfiguration(types=["REGIONAL"])
            ],
            body=open_api_body,
        )

        # aws_api_gateway_deployment
        api_deployment = ApiGatewayDeployment(
            self, "my_api_deployment", rest_api_id=rest_api.id
        )

        # aws_api_gateway_stage
        api_stage = ApiGatewayStage(
            self,
            "my_api_stage",
            deployment_id=api_deployment.id,
            rest_api_id=rest_api.id,
            stage_name="dev",
        )

        # aws_api_gateway_method_settings
        loging_settings = ApiGatewayMethodSettingsSettings(logging_level="ERROR", metrics_enabled=True)
        method_settings = ApiGatewayMethodSettings(
            self,
            "all",
            rest_api_id=rest_api.id,
            stage_name=api_stage.stage_name,
            method_path="*/*",
            settings=[loging_settings],
        )


def main():
    """
    build resources via CDK-TF
    """
    app = App()
    stack = MyApiStack(app, "api-example")
    # configure TF backend to use S3 to store state file
    stack.add_override(
        "terraform.backend",
        {
            "s3": {
                "bucket": tf_bucket_name,
                "key": "terraform-state/api",
                # "region": region,
                "encrypt": True,
            }
        },
    )

    app.synth()


if __name__ == "__main__":
    main()
