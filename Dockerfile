FROM registry.access.redhat.com/rhel8/python-312@sha256:7b98434a7297477d99a8094cf8df0de06cb107b1fd5780c87d08492a306e1756
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
