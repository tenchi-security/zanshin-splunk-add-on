clean:
	rm -f dist/*

cleanAll:
	rm -f dist/*
	docker stop splunk
	docker rm splunk
	docker image rmi splunk/splunk:latest

validate:
	slim validate ./TA-zanshin-add-on-for-splunk

package:
	slim package ./TA-zanshin-add-on-for-splunk -o ./dist

update:
	docker exec -it splunk sudo ./bin/splunk restart

splunk:
	docker pull splunk/splunk:latest
	docker run -d -p 8000:8000 -p 8089:8089 -e "SPLUNK_START_ARGS=--accept-license" -e "SPLUNK_PASSWORD=changeme" --name splunk splunk/splunk:latest

restart:
	docker exec -it splunk sudo ./bin/splunk restart

status:
	docker exec -it splunk sudo ./bin/splunk status

stop:
	docker stop splunk

start:
	docker start splunk
