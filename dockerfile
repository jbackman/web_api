FROM 3.7-alpine
RUN mkdir -p /opt/web
WORKDIR /opt/web
COPY web* ./
RUN python -m pip install -f web-requirements.txt
EXPOSE 8080/tcp
ENTRYPOINT ["/opt/web/web-entry.sh" ]
