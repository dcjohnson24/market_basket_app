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

from . import db, tasks

main = Blueprint('main', __name__)


def generate_rules_from_json() -> Tuple[pd.DataFrame, str]:
    try:
        df = pd.read_sql_table('transactions', con=db.engine)
        metric = request.form.get('metric')
        rules = tasks._rules_from_user_upload.delay(df.to_json(), metric)
        res = rules.wait()
        rules_df = pd.read_json(res)
    except ValueError as ve:
        abort(500, str(ve))

    return rules_df, metric


def before_request():
    with db.engine.connect() as conn:
        conn.execute('DROP TABLE IF EXISTS transactions')
    db.session.commit()


main.before_app_first_request(before_request)


@main.after_request
def after_request(response):
    with app.app_context():
        if app.config['DEBUG']:
            response.headers["Cache-Control"] = (
                "no-cache, no-store, "
                "must-revalidate, public, max-age=0"
            )
            response.headers["Expires"] = 0
            response.headers["Pragma"] = "no-cache"
            return response
    return response


@main.route('/')
def index():
    return render_template('demo.html')


@main.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files.get('file')
    filename = secure_filename(uploaded_file.filename)
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


@main.route('/data_example')
def show_example():
    return render_template('data_example.html')


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
            'tables_demo.html',
            metric=metric,
            table=rules_df.to_html(
                index=False,
                justify='center',
                classes=['table table-bordered table-striped table-hover table-sm'])
        )
    elif viz_type == 'heatmap':
        heatmap = plot_heatmap_plotly(rules_df, metric, show=False)
        return render_template(
            'plotly_output_demo.html',
            plot=heatmap
        )
    else:
        network_graph = plot_network_graph_plotly(rules_df, metric, show=False)
        return render_template(
            'plotly_output_demo.html',
            plot=network_graph
        )


@main.route('/compute_rules', methods=['POST'])
def display_association_rules():
    rules_table, metric = generate_rules_from_json()
    return render_template(
        'tables.html',
        metric=metric,
        table=rules_table.to_html(
            index=False,
            justify='center',
            classes=['table table-bordered table-striped table-hover table-sm']))


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


@main.errorhandler(500)
def internal_error(error):
    return render_template('500.html', error=error), 500
