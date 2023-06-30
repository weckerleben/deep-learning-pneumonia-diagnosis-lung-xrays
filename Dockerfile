FROM python:3.9

WORKDIR /api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx

COPY ./api .

EXPOSE 1796

CMD [ "python", "app.py" ]
