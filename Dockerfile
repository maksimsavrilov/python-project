# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim AS base

EXPOSE 8000
WORKDIR /app
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN python -m pip install -r requirements.txt --root-user-action=ignore

FROM base AS development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
RUN adduser -u 5678 --disabled-password --gecos "" appuser
COPY --chown=appuser:appuser . /app
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
