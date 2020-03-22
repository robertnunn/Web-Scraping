FROM    python:3
LABEL   maintainer="Rob Nunn"

WORKDIR /scraper

COPY    requirements.txt /scraper/
COPY    *.py /scraper/
COPY    *.json /scraper/

RUN     chmod a+x *.py
RUN     pip install -r requirements.txt

CMD     ["./craigslist_scraper.py", "/bin/sh"]
