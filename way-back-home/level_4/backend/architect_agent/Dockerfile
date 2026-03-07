FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY requirements.txt .
RUN uv pip install --no-cache-dir --system -r requirements.txt

COPY . .

EXPOSE 8081

CMD ["python", "server.py"]
