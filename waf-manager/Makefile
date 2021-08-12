# Python code locations
app_code = ./main.py

# ===== CODE LEVEL
#
# codelint -- reformat and find syntax issues
codelint:
	@printf "\n\n\033[0;32m** Static code analysis (pylint) **\n\n\033[0m"
	pipenv run pylint $(app_code)

seclint:
	@printf "\n\n\033[0;32m** Static code security analysis (bandit) **\n\n\033[0m"
	pipenv run bandit $(app_code)


# codecheck -- look for config issues; e.g. missing libraries
codecheck:
	TF_STATE_BUCKET_NAME=bogus pipenv run python -c 'import main'
	pipenv run python -c 'from src.handlers import app'



# ===== RESOURCE LEVEL
#
cdktf_test:
	cdktf synth

build:
	@printf "\n\n\033[0;32m** Synthesize terraform **\n\n\033[0m"
	cdktf get
	cdktf synth

test: clean cdktf_test


apply:
	@printf "\n\n\033[0;32m** Deploy Lambda in cloud **\n\n\033[0m"
	cdktf synth
	cd ./cdktf.out/stacks/waf-manager && terraform init && terraform plan && terraform apply -auto-approve

deploy: clean apply

# ===== PROJECT LEVEL
#
clean:
	rm -rf cdktf.out

destroy:
	cd ./cdktf.out/stacks/waf-manager && terraform destroy -auto-approve
	rm -rf cdktf.out

check:
	cdktf --version