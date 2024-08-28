FROM python:3.10.10

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip

RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT ["python"]

CMD ["manage.py", "runserver", "172.17.0.3:8000"]  