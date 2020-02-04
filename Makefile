BASE_STACK_NAME=slack-git-notify
BUCKET ?= my-bucket-name
BUILD_BUCKET?=source-consolidation

ORGANIZATION?="my-cool-org"

VPC ?= "base--vpc"

ifdef TARGET
	TPL=cloudformation/$(TARGET).yaml
endif


# CloudFormation stacks do not allow underscores but support dashes. Python package names support underscores
# but not dashes. The Stackname contains the component name (or TARGET) which is often the same as the package name.
# To prevent clashes we replace underscores with dashes.
TARGET_TPL=$(subst _,-,$(TARGET))
PACKAGED_TPL=$(TARGET_TPL)-packaged-cloudformation-template.yaml

sync:
	mkdir -p _build/
	cp -R src/* _build/

build:
	rm -rf _build && mkdir -p _build
	pip install --upgrade pip
	pip install -r requirements.txt -t _build
	$(MAKE) sync

package:
	@mkdir -p _build
	@echo "Preparing and uploading AWS package for $(TPL) for $(TARGET_TPL)."
	aws cloudformation package \
		--template-file $(TPL) \
		--s3-bucket $(BUCKET) \
		--s3-prefix packages \
		--output-template-file _build/$(PACKAGED_TPL) \


deploy:
	@echo "Deploying template for $(TPL) for $(TARGET_TPL)."
	aws cloudformation deploy \
		--template-file _build/$(PACKAGED_TPL) \
		--stack-name $(BASE_STACK_NAME)--$(TARGET_TPL)--$(STACK_NAME_SUFFIX) \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			Environment=$(ENV) \
			BucketName=$(BUCKET) \
			Organization=$(ORGANIZATION) \
			GitHubToken=$(GITHUB_TOKEN) \
			VpcName=$(VPC) \

release:
	@$(MAKE) build && $(MAKE) package && $(MAKE) deploy || echo "No changes to be deployed."

clean:
	find . -name "*.pyc" -exec rm -f {} \;
	rm -rf _build

test-coverage:
	PYTHONPATH=./src pytest tests/ --cov=src --full-trace

test:
	PYTHONPATH=./src pytest tests/