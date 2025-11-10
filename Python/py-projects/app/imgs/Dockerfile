FROM python : 3.10.12

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD bash -c "while tru: do spleep1 ; done"