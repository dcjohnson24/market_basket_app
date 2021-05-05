# Market Basket Analysis App

A simple Flask app that serves a `plotly` network graph, heatmap, or table of association rules on user request. The association rules are calculated using [`mlxtend`](http://rasbt.github.io/mlxtend/).

The user will upload data in `.csv`, `.xls`, or `.xlsx` format. The data is expected to contain the columns `InvoiceNo`, `Description`, and `Quantity`. After uploading the data, the user will select the preferred metric for these plots such as 'confidence', 'lift', or 'leverage'.

Note that on a production server, please set `client_max_body_size 50M;` on your`nginx.conf`. Other things that may be worth tweaking are `proxy_read_timeout` and `proxy_connect_timeout`.
