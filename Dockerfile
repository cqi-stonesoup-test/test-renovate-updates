FROM registry.access.redhat.com/ubi9/python-312:9.5@sha256:9b84a91c94aa7e7ebfcd416db7857610bc7872ba6170cfa7b0753590d4b71dd0
ARG author=me
ARG team=me
LABEL simple-python-app.github.com.author=${author} \
      simple-python-app.github.com.team=${team}
WORKDIR /src
COPY app.py .
CMD ["python3", "app.py"]
