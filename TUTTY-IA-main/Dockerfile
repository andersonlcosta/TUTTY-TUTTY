FROM python:3.11-slim

WORKDIR /app

COPY . .

# 🔄 Trocado: removido o google-genai e adicionado o groq
RUN pip install --no-cache-dir groq fastapi uvicorn python-dotenv

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
