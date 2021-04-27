# cdktf-ex
Example of using Terraform CDK



## Intallation:
```bash
# install terraform
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
brew upgrade hashicorp/tap/terraform
# install cdktf
brew install cdktf
# install pipenv
pip3 install --user pipenv

#check
terraform --version
cdktf -h
```


## Pipenv
```bash
pipenv install --dev
pipenv shell
# here install any new packages 
# ... pipenv install pylint --dev
pipenv lock
#  install the last successful environment recorded
pipenv install --ignore-pipfile

# in case we need to uinstall package
pipenv uninstall pylint
```


## Start
- cdktf init --template="python" --local
- edit main.py
- edit cdktf.json
- cdktf get
- cdktf synth

## Clean up
cdktf destroy
