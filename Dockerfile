FROM python:alpine3.12 AS builder
RUN apk add libffi-dev olm-dev musl-dev gcc
RUN pip install "matrix-nio[e2e]" click requests

FROM python:alpine3.12
RUN apk add olm-dev
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --chmod=755 send-message.py /app/send-message.py

ENTRYPOINT ["/app/send-message.py"]