install:
	pip install . --no-deps --upgrade

build_sdist:
	@python setup.py build sdist

deploy: build_sdist
	./deploy_latest.sh

test_deploy: build_sdist
	REPO=pypitest ./deploy_latest.sh

get_version:
	@printf "v"
	@python setup.py --version
