FROM python:alpine3.12 AS builder
RUN apk add libffi-dev olm-dev musl-dev gcc
RUN pip install "matrix-nio[e2e]" click requests
COPY send-message.py /app/send-message.py
RUN chmod +x /app/send-message.py

FROM python:alpine3.12
RUN apk add olm-dev
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=builder /app/send-message.py /app/send-message.py

ENTRYPOINT ["/app/send-message.py"]
