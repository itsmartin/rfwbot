FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apk del .build-deps

COPY rfwbot rfwbot/

CMD ["python", "-u", "-m", "rfwbot", "/etc/rfwbot.json"]
