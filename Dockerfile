FROM python:3.11-slim
WORKDIR /app
COPY . .
EXPOSE 7731
CMD ["python3", "server.py"]
