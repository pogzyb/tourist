tourist-build:
	python3 -m build

tourist-publish-test:
	python3 -m twine upload --repository testpypi dist/*

tourist-publish-pypi:
	python3 -m twine upload dist/*

tourist-local:
	docker compose down
	docker compose up --build tourist-local

tourist-iac-interactive:
	docker compose down
	docker compose up --build -d sam-deploy
	docker exec -it sam-deploy bash
	docker compose down

# tourist-iac-deploy:
# 	docker compose down
# 	docker compose up --build -d sam-deploy
# 	docker exec -it sam-deploy bash
# 	docker compose down
