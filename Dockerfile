FROM registry.access.redhat.com/rhel8/python-312@sha256:cddcd8f0f153676d80657028b2235a59b2f5cfc0fb772be80b12f2f6fe639c97
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
