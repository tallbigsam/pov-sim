FROM grafana/alloy:latest

COPY config.alloy /etc/alloy/config.alloy




ENTRYPOINT ["/bin/alloy"]
CMD ["run", "--stability.level=experimental", "--server.http.listen-addr=0.0.0.0:12345", "--storage.path=/var/lib/alloy/data", "/etc/alloy/config.alloy"]