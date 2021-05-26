"""
sample stack of resources defined with CDK-TF
"""

import importlib
import os
import sys
from pathlib import Path
import inspect
from cdktf import App, TerraformStack, TerraformVariable, TerraformOutput
from constructs import Construct
from imports.aws import AwsProvider
from imports.local import LocalProvider, File
try:
    mymodule = importlib.import_module("imports.terraform_aws_modules.lambda.aws")
except ModuleNotFoundError as err:
    sys.exit(f'{err}: module not found, need to run "cdktf get"')

# constants
region = os.environ["AWS_DEFAULT_REGION"]
tf_bucket_name = os.environ["TF_STATE_BUCKET_NAME"]
project_dir = os.path.dirname(os.path.realpath(__file__))


class MyLambdaStack(TerraformStack):
    """
    sample stack of resources defined with CDK-TF
    """

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here

        self.tags = {"ManagedBy": "terraform CDK", "user": "good.gentleman"}

        self.environment = TerraformVariable(
            self,
            "environment",
            type="string",
            description="The current enviroment being deployed to",
            default="dev"
        )

    def create_lambda(self, service_conf):
        """
        create AWS Lambda funtion
        """
        service_name = service_conf["service_name"]
        handler = service_conf["handler"]

        lambda_funtion = mymodule.TerraformAwsModulesLambdaAws(
            self,
            f"{service_name}-lambda_function",
            source_path=f"{project_dir}/src/handlers",
            function_name=service_name,
            handler=handler,
            runtime="python3.8",
            create_role=True,
            publish=True,
            memory_size=512,
            timeout=30,
            tags=self.tags,
            environment_variables={
                "ENV_VAR1": "terraform CDK",
                "ENV_VAR2": "good.gentleman",
                "Environment_name": "${ var.environment }",
            },
        )

        return lambda_funtion.lambda_function_arn_output

    def create_variables_env_file(self, service_conf):
        """
        provides environment variables that later can be used
        """
        file_contents = ""
        for key in service_conf:
            lambda_name = key
            lambda_arn = service_conf[key]
            file_contents += f"{lambda_name}function_arn={lambda_arn}\n"
            # terraform output
            TerraformOutput(self, f"{lambda_name}_arn", 
                value = lambda_arn
            )

        variable_env_file = File(self, "variable_env_file",
            filename = f"{project_dir}/variables.env",
            content = inspect.cleandoc(file_contents)
        )
        


def main():
    """
    build resources via CDK-TF
    """
    app = App()
    stack = MyLambdaStack(app, "lambda-example")

    lambda_list = [
        {"service_name": "test-1", "handler": "app.lambda_handler"},
        {"service_name": "test-2", "handler": "app.lambda_handler"},
    ]

    lambda_arn_list = {}
    for item in lambda_list:
        lambda_arn = stack.create_lambda(item)
        lambda_name = item["service_name"]
        lambda_arn_list[lambda_name] = lambda_arn
    
    stack.create_variables_env_file(lambda_arn_list)
      
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
