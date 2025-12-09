tourist-build:
	python3 -m build

tourist-publish-test:
	python3 -m twine upload --repository testpypi dist/*

tourist-publish-pypi:
	python3 -m twine upload dist/*
