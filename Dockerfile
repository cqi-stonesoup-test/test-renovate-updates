FROM registry.access.redhat.com/rhel8/python-312@sha256:dee8d28892e1e5734c7a68273ce299456a2d886861753456d28d155d7aa7e8f5
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
