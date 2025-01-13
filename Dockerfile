FROM registry.access.redhat.com/ubi9/python-312:9.5@sha256:88ea2d10c741f169681102b46b16c66d20c94c3cc561edbb6444b0de3a1c81b3
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
