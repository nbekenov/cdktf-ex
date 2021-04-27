#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
from imports.aws import Instance, S3Bucket, AwsProvider


class MyStack(TerraformStack):
  def __init__(self, scope: Construct, ns: str):
    super().__init__(scope, ns)

    AwsProvider(self, 'Aws', region='us-east-1')
    
    helloInstance = Instance(self, 'hello',
      ami="ami-0742b4e673072066f",
      instance_type="t2.micro",
      tags={"Name": "Provisioned by CDKTF", "user": "nathan.bekenov"}
    )
    
    public_ip = TerraformOutput(self, 'hello_public_ip',
      value=helloInstance.public_ip
    )

  def create_bucket(self, bucket_name):
    bucket = S3Bucket(self, 'my_bucket', bucket = bucket_name)
    return bucket
    
  def return_outputs(self, obj):
    TerraformOutput(self, 'bucket_name',
      value=obj.bucket
    )
    


app = App()

stack_obj = MyStack(app, "hello-terraform")
my_bucket_obj = stack_obj.create_bucket(bucket_name = "nathan.bekenov.labs")
stack_obj.return_outputs(my_bucket_obj)

app.synth()




