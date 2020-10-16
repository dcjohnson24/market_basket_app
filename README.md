# Market Basket Analysis App

A simple Flask and React app that serves a `plotly` network graph, heatmap, or table of association rules on user request. The association rules are calculated using [`mlxtend`](http://rasbt.github.io/mlxtend/).

The user will upload data in `.csv`, `.xls`, or `.xlsx` format. The data is expected to contain the columns `InvoiceNo`, `Description`, and `Quantity`. After uploading the data, the user will select the preferred metric for these plots such as 'confidence', 'lift', 'leverage', or 'conviction'.
