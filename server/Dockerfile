FROM python:3.11

EXPOSE 1500

# RUN apt update
# RUN apt install -y libsasl2-dev python-dev libldap2-dev libssl-dev

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

ADD ./ ./

# RUN pip install package_name
CMD ["python", "-u", "./server.py"]
