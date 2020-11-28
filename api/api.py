import sys
import os
from os.path import dirname, abspath, join

sys.path.append(os.pardir)
path = dirname(dirname(abspath(__file__)))
sys.path.append(join(path, 'model'))

from typing import Tuple

from flask import Flask, request, jsonify, redirect, url_for, \
    render_template, abort, Blueprint
from flask import current_app as app
from werkzeug.utils import secure_filename

import pandas as pd

import model.apriori as apriori
from model.visualize import plot_heatmap_plotly, plot_network_graph_plotly

from . import db

main = Blueprint('main', __name__)


def generate_rules_from_json() -> Tuple[pd.DataFrame, str]:
    df = pd.read_sql_table('transactions', con=db.engine)
    metric = request.form.get('metric')
    rules = apriori.rules_from_user_upload(df)
    return rules._asdict()[metric], metric


@main.route('/')
def index():
    return render_template('demo.html')


@main.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files.get('file')
    filename = secure_filename(uploaded_file.filename)
    app.logger.info(f'{filename} has reached here')
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return ".csv, .xls, or .xlsx files only!", 400
        transactions_df = pd.read_excel(uploaded_file.stream)
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
    return '', 204  # This will be routed to completed route by Dropzone


@main.route('/completed')
def completed():
    return render_template('completed.html')


@main.route('/demo_selection')
def demo_selection():
    return render_template('demo_selection.html')


@main.route('/demo', methods=['POST'])
def view_demo():
    metric = request.form.get('metric')
    viz_type = request.form.get('viz_type')
    rules = apriori.run_demo()
    rules_df = rules._asdict()[metric]
    if viz_type == 'table':
        return render_template(
            'tables.html',
            metric=metric,
            table=rules_df.to_html(index=False, classes='rules')
        )
    elif viz_type == 'heatmap':
        heatmap = plot_heatmap_plotly(rules_df, metric, show=False)
        return render_template(
            'plotly_output.html',
            plot=heatmap
        )
    else:
        network_graph = plot_network_graph_plotly(rules_df, metric, show=False)
        return render_template(
            'plotly_output.html',
            plot=network_graph
        )


@main.route('/compute_rules', methods=['POST'])
def display_association_rules():
    rules_table, metric = generate_rules_from_json()
    return render_template(
        'tables.html',
        metric=metric,
        table=rules_table.to_html(index=False, classes='rules'))


@main.route('/heatmap', methods=['POST'])
def plot_heatmap():
    rules_table, metric = generate_rules_from_json()
    heatmap = plot_heatmap_plotly(rules_table, metric, show=False)
    return render_template(
        'plotly_output.html',
        plot=heatmap
    )


@main.route('/network_graph', methods=['POST'])
def plot_network_graph():
    rules_table, metric = generate_rules_from_json()
    network_graph = plot_network_graph_plotly(rules_table, metric, show=False)
    return render_template(
        'plotly_output.html',
        plot=network_graph
    )
