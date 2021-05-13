# Python code locations
app_code = $(shell git ls-files '*.py')

# ===== CODE LEVEL
#
# codelint -- reformat and find syntax issues
codelint:
	pipenv run black $(app_code)
	pipenv run pylint $(app_code)

# codecheck -- look for config issues; e.g. missing libraries
codecheck:
	TF_STATE_BUCKET_NAME=bogus pipenv run python -c 'import main'
	pipenv run python -c 'from src.handlers import app'

# codetest -- call functions, check return values
codetest:
	pipenv run pytest

# ===== RESOURCE LEVEL
#
cdktf_test:
	cdktf diff

build:
	cdktf get
	cdktf synth

test: cdktf_test


deploy:
	cdktf diff
	cdktf deploy --auto-approve

# invoke -- call Lambda in cloud
# XX also check logs
invoke:
	LAMBDA_NAME=$$(aws lambda list-functions | jq -r '.Functions[].FunctionName') \
	; echo $${LAMBDA_NAME} \
	; aws lambda invoke --function-name $${LAMBDA_NAME} /dev/stdout

# ===== PROJECT LEVEL
#
clean:
	cdktf destroy --auto-approve
	rm -rf cdktf.out
	rm -rf imports

check:
	cdktf --version