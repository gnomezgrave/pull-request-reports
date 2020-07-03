BASE_STACK_NAME=pr-notify
BUCKET?=my-bucket
STACK_NAME_SUFFIX?=$(USER)

TEAM=hexmatter
LOGGER=DEBUG

ifdef TARGET
	TPL=cloudformation/$(TARGET).yaml
endif

ifdef ENV
	OWNER=$(TEAM)
	STACK_NAME_SUFFIX=$(ENV)
else
	ENV=development
	OWNER=$(USER)
endif

# CloudFormation stacks do not allow underscores but support dashes. Python package names support underscores
# but not dashes. The Stackname contains the component name (or TARGET) which is often the same as the package name.
# To prevent clashes we replace underscores with dashes.
TARGET_TPL=$(subst _,-,$(TARGET))
PACKAGED_TPL=$(TARGET_TPL)-packaged-cloudformation-template.yaml

sync:
	mkdir -p _build/
	cp -R src/* _build/
	mkdir -p _build/configs
	cp -R configs/ _build/configs/

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
			GitHubToken=$(GITHUB_TOKEN) \
			Owner=$(OWNER) \
			LogLevel=$(LOGGER)

release:
	@$(MAKE) build && $(MAKE) package && $(MAKE) deploy || echo "No changes to be deployed."

clean:
	find . -name "*.pyc" -exec rm -f {} \;
	rm -rf _build
