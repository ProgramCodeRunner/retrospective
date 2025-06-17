FROM python:3.13.4

WORKDIR /app

# Устанавливаем системные зависимости, которых всё ещё может не хватать
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY . .

# Открываем порт (если нужно)
EXPOSE 5000

# Запуск приложения через gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
