"""
sample stack of resources defined with CDK-TF
"""

import importlib
import os
import sys
from pathlib import Path

from cdktf import App, TerraformStack
from constructs import Construct
from imports.aws import AwsProvider

try:
    mymodule = importlib.import_module("imports.terraform_aws_modules.lambda.aws")
except ModuleNotFoundError as err:
    sys.exit(f'{err}: module not found, need to run "cdktf get"')

# constants
region = os.environ["AWS_DEFAULT_REGION"]
tf_bucket_name = os.environ["TF_STATE_BUCKET_NAME"]


class MyLambdaStack(TerraformStack):
    """
    sample stack of resources defined with CDK-TF
    """

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here

        self.tags = {"ManagedBy": "terraform CDK", "user": "good.gentlemen"}

    def create_lambda(self, service_conf):

        service_name = service_conf["service_name"]
        handler = service_conf["handler"]

        source_path = Path(__file__).parent / "src/handlers"
        if not source_path.is_dir():
            sys.exit(f"Handlers missing -- {source_path} not a directory")
            
        print(str(source_path))
        mymodule.TerraformAwsModulesLambdaAws(
            self,
            f"{service_name}-lambda_function",
            source_path=str(source_path),
            function_name=service_name,
            handler=handler,
            runtime="python3.8",
            create_role=True,
            publish=True,
            memory_size = 512,
            timeout = 30,
            tags=self.tags,
            environment_variables = {"ENV_VAR1": "terraform CDK", "ENV_VAR2": "good.gentlemen"}
        )


def main():
    """
    build resources via CDK-TF
    """
    app = App()
    stack = MyLambdaStack(app, "lambda-example")


    lambda_list = [
        {
            "service_name": "test-1",
            "handler" : "app.lambda_handler"
        },
        {
            "service_name": "test-2",
            "handler" : "app.lambda_handler"
        }        
    ]

    for item in lambda_list:
        stack.create_lambda(item)
    # configure TF backend to use S3 to store state file
    stack.add_override(
        "terraform.backend",
        {
            "s3": {
                "bucket": tf_bucket_name,
                "key": "terraform-state/lambda",
                "region": region,
                "encrypt": True,
            }
        },
    )

    app.synth()


if __name__ == "__main__":
    main()
