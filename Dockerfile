FROM registry.access.redhat.com/rhel8/python-312@sha256:4f0e91e3d194e46733849f58c7c574649bf140fb1bec6fe8f36ab1359d2c0f64
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
