FROM python:3.7-alpine
RUN apk update && \
	apk add whois bind-tools
RUN mkdir -p /opt/web
WORKDIR /opt/web
COPY web* ./
RUN pip install --no-cache-dir -r web-requirements.txt && chmod 755 /opt/web/web-entry.sh
EXPOSE 8080/tcp
ENTRYPOINT ["/opt/web/web-entry.sh" ]
