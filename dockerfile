FROM 3.7-alpine
RUN mkdir -p /opt/eb
WORKDIR /opt/web
COPY web* ./
EXPOSE 8080/tcp
ENTRYPOINT ["/opt/web/web-entry.sh" ]
