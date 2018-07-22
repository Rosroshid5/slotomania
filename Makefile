.PHONY: publish
publish: sloto
	rm -rf build dist
	python setup.py bdist_wheel
	twine upload dist/*

.PHONY: test
test:
	PYTHONPATH=. pytest $(filter-out $@,$(MAKECMDGOALS))

.PHONY: setup
setup:
	rm -rf .git/hooks && ln -s $(shell pwd)/git-hooks .git/hooks

.PHONY: sloto
sloto:
	python sloto.py
