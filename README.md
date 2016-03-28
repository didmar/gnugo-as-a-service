# gnugo-as-a-service
A wrapper to use GnuGo through a webservice

## Installing dependencies

    pip install -U flask
    pip install -U flask-cors

## How to use

    python gnugo-as-a-service.py &
    curl http://127.0.0.1:5000/boardsize/13
    curl http://127.0.0.1:5000/play/black/D4
    curl http://127.0.0.1:5000/play/white/k10
    curl http://127.0.0.1:5000/showboard
    ...
