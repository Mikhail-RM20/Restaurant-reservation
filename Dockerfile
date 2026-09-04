FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app/
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /app/requirements.txt

COPY core /app/core/
COPY database /app/database/
COPY main_directory /app/main_directory/
COPY routes /app/routes/
COPY schemas /app/shemas/
COPY services /app/services/
COPY tests /app/tests/


EXPOSE 8001

CMD ["uvicorn", "main_directory.main:app", "--host", "0.0.0.0", "--port", "8001"]