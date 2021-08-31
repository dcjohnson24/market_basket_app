# Market Basket Analysis App

A simple Flask app that serves a `plotly` network graph, heatmap, or table of association rules on user request. The association rules are calculated using [`mlxtend`](http://rasbt.github.io/mlxtend/).

The user will upload data in `.csv`, `.xls`, or `.xlsx` format. The data is expected to contain the columns `InvoiceNo`, `Description`, and `Quantity`. After uploading the data, the user will select the preferred metric for these plots such as 'confidence', 'lift', or 'leverage'.

## Random production stuff

Note that on a production server, please set `client_max_body_size 50M;` on your `nginx.conf`. Other things that may be worth tweaking are `proxy_read_timeout` and `proxy_connect_timeout`.

The `sqlite` database is stored in `/tmp` for now. Until a better place is found, the permissions for the db files here must be changed with `chmod 666 /tmp/prod.db`.

The `redis.conf` should be edited as follows: `daemonize yes` and `supervised no`. The `redis` server will start once the server is running.

Remember to create a `.env` file with the following attributes e.g.
```
DEV_DATABASE_URI=sqlite:///dev.db
PROD_DATABASE_URI=sqlite:///prod.db
FLASK_ENV=production
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

Install `letsencrypt` and `certbot` on your machine. To keep the certificates automatically renewed, set up a cron job like so:

```bash
crontab -e
```

When the editor opens, add the line `0 0 1 */2 * /usr/bin/letsencrypt renew >> /var/log/letsencrypt-renew.log`, which will renew the certificates every two months at 00:00 on the first day of the month.
