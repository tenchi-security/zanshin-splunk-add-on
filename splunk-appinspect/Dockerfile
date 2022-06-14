FROM python:3.8.13-slim

VOLUME /src

RUN apt-get update
RUN apt-get install -y libmagic-dev python-dev libxml2 libxml2-dev libxslt-dev
RUN pip install splunk-appinspect

WORKDIR /src

RUN mkdir -p report

CMD splunk-appinspect inspect --max-messages=all /src/app/ --mode test --included-tags splunk_appinspect --data-format json --output-file /src/report/results.json
