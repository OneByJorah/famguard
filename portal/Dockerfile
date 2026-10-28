FROM python:3.12-alpine

WORKDIR /app
COPY server.py .
COPY index.html .
COPY qrcode.min.js .

RUN adduser -D -u 1001 portal && chown -R portal:portal /app
USER portal

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1

CMD ["python", "server.py"]
