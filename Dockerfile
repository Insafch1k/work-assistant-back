# 1) База всегда первой строкой
FROM python:3.12-slim

# 2) Создаём системных пользователя/группу (ещё под root)
RUN groupadd --system appgroup \
 && useradd --system --no-create-home --gid appgroup --shell /usr/sbin/nologin appuser

# 3) Создаем директории для медиа файлов ЕЩЁ ПОД ROOT
RUN mkdir -p /media \
 && mkdir -p /media/avatars \
 && mkdir -p /media/uploads \
 && chown -R appuser:appgroup /media \
 && chmod -R 755 /media

RUN python -m pip install --upgrade pip setuptools wheel

# 4) Директория приложения
WORKDIR /app

# 5) Ставим зависимости (кешируем по requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6) Копируем код и выдаём права пользователю
COPY . .
RUN chown -R appuser:appgroup /app

# 7) Запускаем не из-под root
USER appuser

EXPOSE 5000
CMD ["gunicorn", \
     "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", \
     "-w", "1", \
     "-b", "0.0.0.0:5000", \
     "app:app"]