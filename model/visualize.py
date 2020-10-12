import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import plotly.graph_objects as go


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

