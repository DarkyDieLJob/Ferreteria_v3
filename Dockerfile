FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=America/Argentina/Buenos_Aires

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /Ferreteria_v3

COPY requirements.txt /Ferreteria_v3/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /Ferreteria_v3/

RUN mkdir -p /Ferreteria_v3/logs /Ferreteria_v3/media /Ferreteria_v3/static

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
