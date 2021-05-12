# CDKTF-lambda-example
> Example how to deploy AWS lambda with CDKTF

## Prerequisites
* Terraform v0.12+
* cdktf
* Node.js v12.16+
* Python v3.7+ and pipenv
* AWS account and AWS Access Credentials

## Usage
```bash
git clone https://github.com/NursultanBeken/cdktf-ex.git
cd lambda-example
export AWS_DEFAULT_REGION=<your region>
export TF_STATE_BUCKET_NAME=<name of s3 bucket where state file will be created>

make build
make deploy
```

## Cleanup
> make clean