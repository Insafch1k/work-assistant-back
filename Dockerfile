# 1) База всегда первой строкой
FROM python:3.12-slim

# 2) Создаём системных пользователя/группу (ещё под root)
RUN groupadd --system appgroup \
 && useradd --system --no-create-home --gid appgroup --shell /usr/sbin/nologin appuser

RUN python -m pip install --upgrade pip setuptools wheel
# 3) Директория приложения
WORKDIR /app

# 4) Ставим зависимости (кешируем по requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Копируем код и выдаём права пользователю
COPY . .
RUN chown -R appuser:appgroup /app

# 6) Запускаем не из-под root
USER appuser

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
