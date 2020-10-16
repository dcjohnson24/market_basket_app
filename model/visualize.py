import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import plotly.graph_objects as go

from addEdge import addEdge


def remove_frozensets(rules: pd.DataFrame) -> pd.DataFrame:
    """ Convert frozen sets from mlxtend to comma separated lists

    Args:
        rules (pd.DataFrame): assocation rules generated
            with association_rules function of mlxtend

    Returns:
        pd.DataFrame: DataFrame with antecendents and consequents columns
            of type list.
    """
    rules['antecedents_'] = rules['antecedents'].apply(
        lambda a: ','.join(list(a))
    )
    rules['consequents_'] = rules['consequents'].apply(
        lambda a: ','.join(list(a))
    )
    rules['antecedents_'] = rules['antecedents_'].str.strip()
    rules['consequents_'] = rules['consequents_'].str.strip()

    return rules


def plot_heatmap_plotly(rules: pd.DataFrame, plot_val: str) -> None:
    """ Plot an interactive heatmap

    Args:
        rules (pd.DataFrame): association rules from mlxtend
        plot_val (str): The metric to use for the heatmap such as
            confidence, lift, or leverage
    """
    rules = remove_frozensets(rules)

    fig = go.Figure(data=go.Heatmap(
        x=rules['antecedents_'],
        y=rules['consequents_'],
        z=rules[plot_val],
        hoverongaps=False
    ))

    fig.update_layout(
        title=f'{plot_val}'.title(),
        xaxis_title='Antecedents',
        yaxis_title='Consequents'
    )
    fig.show()


def plot_heatmap_seaborn(rules: pd.DataFrame, plot_val: str) -> None:
    """ Plot a static heatmap

    Args:
        rules (pd.DataFrame): association rules from mlxtend
        plot_val (str): The metric to use for the heatmap such as
            confidence, lift, or leverage
    """
    rules = remove_frozensets(rules)
    pivot = rules.pivot(
        index='antecedents_',
        columns='consequents_',
        values=plot_val
    )
    sns.heatmap(pivot, annot=True)
    plt.yticks(rotation=0)
    plt.xticks(rotation=90)
    plt.xlabel('Consequents')
    plt.ylabel('Antecedents')
    plt.title(f'{plot_val}'.title())
    plt.tight_layout()
    plt.show()


def plot_network_graph_plotly(rules: pd.DataFrame, weight_var: str) -> None:
    """ Create a network of items and rules where edges contain
    various scores such as confidence, lift, etc.

    Args:
        rules (pd.DataFrame): DataFrame of association rules from mlxtend
        weight_var (str): the association metric to use. Must be one of 
            'confidence', 'lift', 'leverage', or 'conviction'.
    """
    rules = remove_frozensets(rules)
    rules[f'{weight_var}'] = rules[f'{weight_var}'].round(2)

    G1 = nx.from_pandas_edgelist(
        rules,
        source='antecedents_',
        target='consequents_',
        edge_attr=f'{weight_var}',
        create_using=nx.DiGraph
    )
    pos = nx.spring_layout(G1, k=0.5)
    for n, p in pos.items():
        G1.nodes[n]['pos'] = p

    xmids = []
    ymids = []
    edge_x = []
    edge_y = []

    for edge in G1.edges():
        x0, y0 = G1.nodes[edge[0]]['pos']
        x1, y1 = G1.nodes[edge[1]]['pos']
        xmids.append((x0 + x1)/2)
        ymids.append((y0 + y1)/2)
        edge_x, edge_y = addEdge(
            start=(x0, y0),
            end=(x1, y1),
            edge_x=edge_x,
            edge_y=edge_y,
            arrowPos='end',
            arrowLength=0.04
        )

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    etext = [f'{weight_var}: {w}' for w in
             list(nx.get_edge_attributes(G1, f'{weight_var}').values())]

    eweights_trace = go.Scatter(
        x=xmids,
        y=ymids,
        mode='markers',
        marker=dict(color='rgb(125,125,125)', size=1),
        text=etext,
        hoverinfo='text'
    )

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=list(G1.nodes),
        mode='markers',
        hoverinfo='text',
        marker_size=15,
        marker_color='#000080'
    )

    for node in G1.nodes():
        x, y = G1.nodes[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    fig = go.Figure(
        data=[edge_trace, node_trace, eweights_trace],
        layout=go.Layout(
            title=f'<b>Retail Items Network Connections'
                  f' based on {weight_var} score </b>',
            titlefont=dict(size=16),
            title_x=0.5,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    fig.add_annotation(
        text=f'<b>Note:</b> Hover over node to get name of item<br>'
             f' Hover over edge arrow between'
             f' nodes to get {weight_var} score<br>'
             f' Arrow represents rule A &#8594; C'
    )
    fig.show()
