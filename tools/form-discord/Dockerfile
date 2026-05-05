FROM python:3.11-slim

RUN apt-get update && apt-get install -y fonts-noto-cjk && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r tools/form-discord/requirements.txt

CMD ["gunicorn", "--chdir", "tools/form-discord", "--bind", "0.0.0.0:10000", "form_discord_web:app"]
