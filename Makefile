.PHONY: publish
publish:
	rm -rf build dist
	python setup.py bdist_wheel
	twine upload dist/*

.PHONY: test
test:
	pytest $(filter-out $@,$(MAKECMDGOALS))
