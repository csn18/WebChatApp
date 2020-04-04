FROM python:3.8-slim

COPY . .

RUN pip install --no-cache-dir Flask && \
    pip install --no-cache-dir mysql-connector && \
    pip install --no-cache-dir PyJWT && \
    pip install --no-cache-dir flask_socketio


EXPOSE 5000

CMD ["python3", "app.py"]