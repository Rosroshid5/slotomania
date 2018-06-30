.PHONY: publish
publish:
	rm -rf build dist
	python setup.py bdist_wheel
	twine upload dist/*

.PHONY: test
test:
	pytest $(filter-out $@,$(MAKECMDGOALS))

.PHONY: setup
setup:
	rm -rf .git/hooks && ln -s $(shell pwd)/git-hooks .git/hooks
