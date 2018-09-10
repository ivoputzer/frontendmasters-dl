FROM python:2.7-alpine3.7

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.7/main" >> /etc/apk/repositories \
 && echo "http://dl-4.alpinelinux.org/alpine/v3.7/community" >> /etc/apk/repositories \
 && apk update \
 && apk add chromium chromium-chromedriver

USER root
WORKDIR /app/src

COPY OS_FrontendMaster-dl/ /app/src/
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "frontendmasters-dl.py"]
CMD ["--help"]
