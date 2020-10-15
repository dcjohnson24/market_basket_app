import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import plotly.graph_objects as go
from d3graph import d3graph, vec2adjmat


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


def plot_network_graph_d3(rules: pd.DataFrame, weight_var: str) -> None:
    rules = remove_frozensets(rules)
    adjmat = vec2adjmat(source=rules['antecedents_'],
                        target=rules['consequents_'])
    node_size = rules[f'{weight_var}'].tolist()
    d3graph(adjmat, node_size_edge=node_size, directed=True)


def plot_network_graph(rules: pd.DataFrame, weight_var: str) -> None:
    rules = remove_frozensets(rules)
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

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    xmids = []
    ymids = []

    for edge in G1.edges():
        x0, y0 = G1.nodes[edge[0]]['pos']
        x1, y1 = G1.nodes[edge[1]]['pos']
        xmids.append((x0 + x1)/2)
        ymids.append((y0 + y1)/2)
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    etext = [f'weight: {w}' for w in
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
        marker_color='RoyalBlue'
    )

    for node in G1.nodes():
        x, y = G1.nodes[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    fig = go.Figure(
        data=[edge_trace, node_trace, eweights_trace],
        layout=go.Layout(
            title='<br>Retail Items Network Connections',
            titlefont=dict(size=16),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )
    fig.show()


def draw_graph(rules: pd.DataFrame, rules_to_show: int) -> None:
    G1 = nx.DiGraph()
    color_map = []
    N = 50
    colors = np.random.rand(N)
    strs = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5',
            'R6', 'R7', 'R8', 'R9', 'R10', 'R11']

    for i in range(rules_to_show):
        G1.add_nodes_from(["R"+str(i)])
        for a in rules.iloc[i]['antecedents']:
            G1.add_nodes_from([a])
            G1.add_edge(a, "R"+str(i), color=colors[i], weight=2)
        for c in rules.iloc[i]['consequents']:
            G1.add_nodes_from([c])
            G1.add_edge("R"+str(i), c, color=colors[i],  weight=2)

    for node in G1:
        found_a_string = False
        for item in strs:
            if node == item:
                found_a_string = True
        if found_a_string:
            color_map.append('yellow')
        else:
            color_map.append('green')

    edges = G1.edges()
    colors = [G1[u][v]['color'] for u, v in edges]
    weights = [G1[u][v]['weight'] for u, v in edges]

    pos = nx.spring_layout(G1, k=16, scale=1)
    nx.draw(G1, pos, node_color=color_map,
            edge_color=colors, width=weights, font_size=16,
            with_labels=False)

    for p in pos:  # raise text positions
        pos[p][1] += 0.07
    nx.draw_networkx_labels(G1, pos)
    plt.show()
