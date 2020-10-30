import sys
import os
from os.path import dirname, abspath, join

sys.path.append(os.pardir)
path = dirname(dirname(abspath(__file__)))
sys.path.append(join(path, 'model'))

from flask import Flask, request, jsonify, redirect, url_for, \
    render_template, abort, Blueprint
from flask import current_app as app
from werkzeug.utils import secure_filename

import pandas as pd

import model.apriori as apriori
from model.visualize import plot_heatmap_plotly, plot_network_graph_plotly

from . import db

main = Blueprint('main', __name__)


# TODO create a database so that once the data is uploaded it
# can be passed around.
# Figure out better display method of Pandas DataFrame.
@main.route('/')
def index():
    return render_template('index.html')


@main.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files.get('file')
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        app.logger.info('Loading into pandas dataframe')
        transactions_df = pd.read_excel(uploaded_file.stream)
        app.logger.info('Loading into Sqllite')
        transactions_df.to_sql(
            'transactions',
            con=db.engine,
            if_exists='replace',
            index=False,
            chunksize=500,
            dtype={
                'InvoiceNo': db.String,
                'Description': db.String,
                'Quantity': db.Integer
            }
        )
        app.logger.info('Done!')
        app.logger.info(f'transactions_df.shape={transactions_df.shape}')
        return redirect(url_for('main.completed'))
    return render_template('index.html')


@main.route('/completed')
def completed():
    return render_template('completed.html')


@main.route('/demo', methods=['GET'])
def view_demo():
    metric = request.get_json()['metric']
    rules = apriori.run_retail_demo()
    print(rules._asdict()[metric])


@main.route('/compute_rules', methods=['GET', 'POST'])
def display_association_rules():
    df = pd.read_sql_table('transactions', con=db.engine)
    metric = request.form.get('metric')
    app.logger.info(f'metric uploaded as {metric}')
    rules = apriori.rules_from_user_upload(df)
    # TODO display rules_dict[metric] as DataFrame to user
    rules_table = rules._asdict()[metric]
    app.logger.info(f'{rules_table}')
    return render_template(
        'tables.html',
        metric=metric,
        table=rules_table.to_html(index=False, classes='rules'))


@main.route('/heatmap', methods=['GET'])
def plot_heatmap():
    req = request.files.get('file')
    metric = request.get_json()['metric']
    rules = apriori.rules_from_user_upload(req)
    plot_heatmap_plotly(rules._asdict[metric], metric)


@main.route('/network_graph', methods=['GET'])
def plot_network_graph():
    req = request.files.get('file')
    metric = request.get_json()['metric']
    rules = apriori.rules_from_user_upload(req)
    plot_network_graph_plotly(rules._asdict()[metric], metric)


@main.errorhandler(413)
def too_large(error):
    return "File is too large", 413


@main.errorhandler(400)
def wrong_type(error):
    return render_template('400.html'), 400
