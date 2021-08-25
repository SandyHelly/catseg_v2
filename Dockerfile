FROM ubuntu:latest
EXPOSE 5000
ENV TZ=Europe/Moscow
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone &&\
	apt-get update -y &&\
	apt-get install -y python3-pip python3-dev build-essential &&\
	apt-get install libgl1-mesa-glx -y &&\
	apt-get install libgtk2.0-dev -y &&\
	pip3 install -r requirements.txt
ENTRYPOINT ["./gunicorn.sh"]