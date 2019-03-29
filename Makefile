###
# KMS Service is an AWS Lambda interface to interact with AWS KMS Key Encryption
# service.
# 
# Copyright (C) 2018-2019  Asurion, LLC
#
# KMS Service is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KMS Service is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KMS Service.  If not, see <https://www.gnu.org/licenses/>.
###
PYVERSION ?= 3.6
APP_NAME = kms-service-lambda

.PHONY: build
build:
	@python3 --version 2>&1 | grep $(PYVERSION)
	@mkdir dist target
	@cp -r *.py requirements.txt dist/
	@pip3 install -r requirements.txt -t dist
	@find dist/ -type f -name "*.py[co]" -exec rm {} +
	@cd dist && zip -r $(APP_NAME).zip *
	@cd ..
	@mv dist/$(APP_NAME).zip target/$(APP_NAME).zip
	@rm -rf dist/
	@echo "Deployment package is ready at target/$(APP_NAME).zip"