FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/main.py

COPY ./app /code/app

EXPOSE 80

CMD ["fastapi", "run", "main.py", "--port", "80"]
