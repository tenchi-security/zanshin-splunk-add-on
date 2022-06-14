FROM splunk/splunk:latest

COPY /TA-zanshin-add-on-for-splunk /opt/splunk/etc/apps/TA-zanshin-add-on-for-splunk

ENV SPLUNK_USER=root
ENV SPLUNK_START_ARGS=--accept-license
ENV SPLUNK_PASSWORD=changeme
