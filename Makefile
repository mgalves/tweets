export PROJ_URI=tweets
export IMAGE=tweets
export ROOT_DIR=${PWD}


VERSION ?= $(shell date +"%Y%m%d_%H%M")

build:
	docker build -t ${IMAGE} -f Dockerfile .

shell:
	docker run --rm -ti --network tweets_default --env-file etc/env -v ${ROOT_DIR}/src:/opt/tweets -v ${ROOT_DIR}/datasets:/opt/datasets ${IMAGE} /bin/sh

grabber:
	docker run --rm -ti --network tweets_default --env-file etc/env -v ${ROOT_DIR}/src:/opt/tweets -v ${ROOT_DIR}/datasets:/opt/datasets ${IMAGE} /opt/tweets/cmd_run_grabber.sh

processor:
	docker run --rm -ti --network tweets_default --env-file etc/env -v ${ROOT_DIR}/src:/opt/tweets -v ${ROOT_DIR}/datasets:/opt/datasets ${IMAGE} /opt/tweets/cmd_run_processor.sh
	
clean:
	docker run --rm -ti --network tweets_default --env-file etc/env -v ${ROOT_DIR}/src:/opt/tweets -v ${ROOT_DIR}/datasets:/opt/datasets ${IMAGE} /opt/tweets/cmd_clean.sh

report:
	docker run --rm -ti --network tweets_default --env-file etc/env -v ${ROOT_DIR}/src:/opt/tweets -v ${ROOT_DIR}/datasets:/opt/datasets ${IMAGE} /opt/tweets/cmd_run_report.sh
	
