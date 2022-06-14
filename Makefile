APP=TA-zanshin-add-on-for-splunk

SPLUNK_IMAGE=splunk/zanshin-add-on

APPINSPECT=splunk-appinspect
APPINSPECT_IMAGE=zanshin-splunk-appinspect

VERSION=$(shell grep '^version' ${APP}/default/app.conf | egrep -o '[^ ]+$$')
BUILD=$(shell grep '^build' ${APP}/default/app.conf | egrep -o '[^ ]+$$')
FILE=${APP}-${VERSION}-${BUILD}.spl

splunk-build:
	@if [ ! "$$(docker images ${SPLUNK_IMAGE})"]; then \
		docker build -t ${SPLUNK_IMAGE} . ; \
	else \
		echo "${SPLUNK_IMAGE} build already exists!" ; \
	fi

splunk-up: splunk-build
	@if [ ! "$$(docker ps -qa -f name=${APP})"]; then \
		docker run \
		-d \
		--name ${APP} \
		--hostname ${APP} \
		--publish 8000:8000 \
		--publish 8088:8088 \
		--publish 8089:8089 \
		${SPLUNK_IMAGE} ; \
	elif [ ! "$$(docker ps -q -f name=${APP})"]; then \
		docker start ${APP}; \
	else \
		echo "${APP} already started!" ; \
	fi

splunk-down:
	docker stop ${APP}

splunk-clean:
	docker kill ${APP}
	docker rm -v ${APP}

splunk-update: app-update splunk-restart

splunk-logs:
	docker logs -f ${APP}

splunk-log-alerts:
	docker exec -it ${APP} sudo cat ./var/log/splunk/ta_zanshin_add_on_for_splunk_zanshin_alerts.log

splunk-log-following-alerts:
	docker exec -it ${APP} sudo cat ./var/log/splunk/ta_zanshin_add_on_for_splunk_zanshin_following_alerts.log

splunk-bash:
	docker exec -it ${APP} bash

splunk-restart:
	docker exec -it ${APP} sudo ./bin/splunk restart

splunk-status:
	docker exec -it ${APP} sudo ./bin/splunk status

splunk-inspect: aadd-on-inspect

splunk-package: add-on-package

add-on-update:
	docker exec -it ${APP} sudo cp -r ./etc/apps/${APP}/local ./etc/apps/zanshintemp
	docker exec -it ${APP} sudo rm -rf ./etc/apps/${APP}
	docker cp ${APP} ${APP}:/opt/splunk/etc/apps/${APP}
	docker exec -it ${APP} sudo cp -r ./etc/apps/zanshintemp ./etc/apps/${APP}/local
	docker exec -it ${APP} sudo rm -rf ./etc/apps/zanshintemp

add-on-package:
	mkdir -p out
	tar -cvzf out/${FILE} ${APP}

add-on-inspect-bash:
	docker exec -it ${APPINSPECT} bash

add-on-inspect-build:
	docker build -t ${APPINSPECT_IMAGE} ./${APPINSPECT}

add-on-inspect-start: add-on-inspect-build
	docker run \
		-d \
		--name ${APPINSPECT} \
		--hostname ${APPINSPECT} \
		--volume $(shell pwd)/${APP}:/src/app/${APP} \
		--volume $(shell pwd)/splunk-appinspect/report:/src/report \
		--rm ${APPINSPECT_IMAGE}

add-on-inspect-logs:
	docker logs -f ${APPINSPECT}

add-on-inspect: app-inspect-start app-inspect-logs

