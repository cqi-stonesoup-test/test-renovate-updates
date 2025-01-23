FROM registry.access.redhat.com/ubi9/python-312:9.5-1737522330@sha256:b642db8b1f0f9dca7bbe6999db7ac4c96cf3036833fc344af092268afbb02893
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
