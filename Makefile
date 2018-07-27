.PHONY: publish
publish:
	rm -rf build dist
	python setup.py bdist_wheel
	twine upload dist/*

.PHONY: test
test:
	PYTHONPATH=. pytest $(filter-out $@,$(MAKECMDGOALS))

.PHONY: coverage
coverage: ## Generate a test coverage report based on `manage.py test`
	open .cover/index.html
	PYTHONPATH=. pytest --cov . --cov-report term-missing --cov-report html:.cover \
	   	--cov-fail-under=100 $(filter-out $@,$(MAKECMDGOALS))

.PHONY: setup
setup:
	rm -rf .git/hooks && ln -s $(shell pwd)/git-hooks .git/hooks
