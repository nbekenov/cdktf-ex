# Python code locations
app_code = ./main.py

codelint:
	pylint $(app_code)

cdktf_test:
	cdktf synth
	cdktf diff

build:
	cdktf get
	cdktf synth

test: cdktf_test


deploy:
	cdktf diff
	cdktf deploy --auto-approve

clean:
	cdktf destroy --auto-approve
	rm -rf cdktf.out
	rm -rf imports