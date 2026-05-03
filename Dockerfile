FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

COPY . .

EXPOSE 8000

CMD ["gunicorn", "hotel_reservation.wsgi:application", "--config", "gunicorn.conf.py"]
