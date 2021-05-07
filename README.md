# Market Basket Analysis App

A simple Flask app that serves a `plotly` network graph, heatmap, or table of association rules on user request. The association rules are calculated using [`mlxtend`](http://rasbt.github.io/mlxtend/).

The user will upload data in `.csv`, `.xls`, or `.xlsx` format. The data is expected to contain the columns `InvoiceNo`, `Description`, and `Quantity`. After uploading the data, the user will select the preferred metric for these plots such as 'confidence', 'lift', or 'leverage'.

## Random production stuff

Note that on a production server, please set `client_max_body_size 50M;` on your`nginx.conf`. Other things that may be worth tweaking are `proxy_read_timeout` and `proxy_connect_timeout`.

The `sqlite` database is stored in `/tmp` for now. Until a better place is found, the permissions for the db files here must be changed with `chmod 666 /tmp/prod.db`.

The `redis.conf` should be edited as follows: `daemonize yes` and `supervised no`. The `redis` server will start once the server is running.
