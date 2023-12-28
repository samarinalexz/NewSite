FROM python:3.11


SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
    libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales vim

RUN useradd -rms /bin/bash yt && cgmod 777 /opt /run

WORKDIR /yt

RUN mkdir /yt/static && mkdir /yt/media && chown -R yt:yt /yt && chmod 755 /yt

COPY --chown=yt:yt . .

RUN pip install -r requirements.txt

USER yt

CMD ["manage.py","runserver","bulletin_board.wsgi:application"]
