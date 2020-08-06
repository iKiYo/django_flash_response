# Docker file for production enviironment
FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

# copy the package list file of pipenv environment
# and install them directly to the server
COPY Pipfile Pipfile.lock /code/ 
RUN pip install 'pipenv==2018.11.26' && pipenv install --system

COPY . /code/
            
# install gettext for annotations of internatilization 
RUN apt-get update \
	&& apt-get install -y gettext --no-install-recommends \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# create a user and execute as the user
# ENV USER=fr_app_admin
# RUN groupadd --system fr_app\
# 	&& useradd --no-log-init --create-home --system --gid fr_app ${USER}
# USER ${USER}
