# Python code locations
app_code = $(shell git ls-files '*.py')

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

# codetest -- call functions, check return values
codetest:
	@printf "\n\n\033[0;32m** Unit testing (pytest) **\n\n\033[0m"
	pipenv run pytest

# ===== RESOURCE LEVEL
#
cdktf_test:
	cdktf diff

build:
	@printf "\n\n\033[0;32m** Synthesize terraform **\n\n\033[0m"
	cdktf get
	cdktf synth

test: codelint  codetest cdktf_test


deploy:
	@printf "\n\n\033[0;32m** Deploy Lambda in cloud **\n\n\033[0m"
	cdktf diff
	cdktf deploy --auto-approve

# invoke -- call Lambda in cloud
# XX also check logs
invoke:
	@printf "\n\n\033[0;32m** call Lambda in cloud **\n\n\033[0m"
	LAMBDA_NAME=$$(aws lambda list-functions | jq -r '.Functions[].FunctionName') \
	; echo $${LAMBDA_NAME} \
	; aws lambda invoke --function-name $${LAMBDA_NAME} /dev/stdout

# ===== PROJECT LEVEL
#
clean:
	rm -rf cdktf.out

check:
	cdktf --version