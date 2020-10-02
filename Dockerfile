FROM python:alpine3.12 AS builder
RUN apk add libffi-dev olm-dev musl-dev gcc
RUN pip install "matrix-nio[e2e]"

FROM python:alpine3.12
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY send-message.py /app/send-message.py