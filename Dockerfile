FROM registry.access.redhat.com/rhel8/python-312@sha256:5bc39ac967491e7ca7d8c8a44338b2d4df1990b7ef769b29d459e3ca8744800e
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
