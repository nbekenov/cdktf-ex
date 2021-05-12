import os, inspect
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, S3Backend, TerraformVariable
from imports.aws import AwsProvider
import importlib
#from imports.terraform_aws_modules.lambda.aws import TerraformAwsModulesLambdaAws will fail cause path contains key word
# Import a module from a path that contains a reserved Python keyword like
mymodule = importlib.import_module('imports.terraform_aws_modules.lambda.aws')


region = os.environ.get("AWS_DEFAULT_REGION")
tf_bucket_name = os.environ.get("TF_STATE_BUCKET_NAME")
dir_path = os.path.dirname(os.path.realpath(__file__))

class MyLambdaStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # define resources here
        AwsProvider(self, 'Aws', region='us-east-1')

        tags = {
            "ManagedBy" : "terraform CDK",
            "user" : "good.gentlemen"
        }

        my_lambda_function = mymodule.TerraformAwsModulesLambdaAws(self, "my_lambda_function",
            source_path = f"{dir_path}/src/handlers",
            function_name = "my-test-lambda",
            description   = "Simple hello world deployed by Terraform",
            handler = "app.lambda_handler",
            runtime = "python3.8",
            create_role = True,
            publish     = True,
            tags = tags
        )

app = App()
stack = MyLambdaStack(app, "lambda-example")
# configure TF backend to use S3 to store state file
stack.add_override(
  "terraform.backend", {
      "s3": {
        "bucket": tf_bucket_name,
        "key": "terraform-state/lambda",
        "region": region,
        "encrypt": True
        }
  }
)

app.synth()
