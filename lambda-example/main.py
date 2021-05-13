"""
sample stack of resources defined with CDK-TF
"""

import importlib
import os
import sys
from pathlib import Path

from cdktf import App, TerraformStack
from constructs import Construct

# from imports.aws import AwsProvider

# from imports.terraform_aws_modules.lambda.aws import
# TerraformAwsModulesLambdaAws will fail cause path contains key word Import a
# module from a path that contains a reserved Python keyword like
try:
    mymodule = importlib.import_module("imports.terraform_aws_modules.lambda.aws")
except ModuleNotFoundError as err:
    sys.exit(f'{err}: module not found, need to run "cdktf get"')

# constants
# region = os.environ["AWS_DEFAULT_REGION"]
tf_bucket_name = os.environ["TF_STATE_BUCKET_NAME"]


class MyLambdaStack(TerraformStack):
    """
    sample stack of resources defined with CDK-TF
    """

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        # AwsProvider(self, "Aws", region=region)

        tags = {"ManagedBy": "terraform CDK", "user": "good.gentlemen"}

        source_path = Path(__file__).parent / "src/handlers"
        if not source_path.is_dir():
            sys.exit(f"Handlers missing -- {source_path} not a directory")

        mymodule.TerraformAwsModulesLambdaAws(
            self,
            "my_lambda_function",
            source_path=str(source_path),
            function_name="my-test-lambda",
            description="Simple hello world deployed by Terraform",
            handler="app.lambda_handler",
            runtime="python3.8",
            create_role=True,
            publish=True,
            tags=tags,
        )


def main():
    """
    build resources via CDK-TF
    """
    app = App()
    stack = MyLambdaStack(app, "lambda-example")
    # configure TF backend to use S3 to store state file
    stack.add_override(
        "terraform.backend",
        {
            "s3": {
                "bucket": tf_bucket_name,
                "key": "terraform-state/lambda",
                # "region": region,
                "encrypt": True,
            }
        },
    )

    app.synth()


if __name__ == "__main__":
    main()
