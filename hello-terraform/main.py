#!/usr/bin/env python
import os
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from imports.aws import Instance, S3Bucket, AwsProvider

tf_bucket_name = os.getenv("S3_BUCKET_NAME", "nathan.bekenov.labs")

class MyStack(TerraformStack):
  def __init__(self, scope: Construct, ns: str):
    super().__init__(scope, ns)

    AwsProvider(self, 'Aws', region='us-east-1')
    
    # create EC2 instance
    helloInstance = Instance(self, 'hello',
      ami="ami-0742b4e673072066f",
      instance_type="t2.micro",
      tags={"Name": "Provisioned by CDKTF", "user": "nathan.bekenov"}
    )
    # create S3 bucket
    bucket = S3Bucket(self, 'my_bucket', bucket = "nathan.bekenov.labs")
    
    # Outputs
    public_ip = TerraformOutput(self, 'hello_public_ip',
      value=helloInstance.public_ip
    )

    bucket_name = TerraformOutput(self, 'hello_bucket_name',
      value=bucket.bucket
    )


if __name__=="__main__":
  app = App()
  stack = MyStack(app, "hello-terraform")

  # configure TF backend to use S3 to store state file
  stack.add_override(
    "terraform.backend", {
        "s3": {
          "bucket": tf_bucket_name,
          "key": "terraform-state/dev",
          "region": 'us-east-1',
          "encrypt": "true"
          }
    }
  )

  app.synth()





