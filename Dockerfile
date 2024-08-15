FROM registry.access.redhat.com/rhel8/python-312@sha256:f64e62f892dd02a1e311ff67be9fb7f4e244d2ff0654fe937efb3f4da248723f
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
