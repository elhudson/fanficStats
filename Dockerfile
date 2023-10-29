FROM python:3.11.6
WORKDIR /project
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .