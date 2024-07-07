FROM python:3.9

WORKDIR /code
 
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/main.py
COPY ./app /code/app

EXPOSE 8080

CMD ["uvicorn", "main", "--host", "0.0.0.0", "--port", "8080"]
