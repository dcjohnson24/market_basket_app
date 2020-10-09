import pandas as pd

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth, association_rules

import visualize


def read_input_data(file_name: str) -> pd.DataFrame:
    """ Check whether data is .csv, .xls, or .xlsx extension.

    Args:
        file_name (str): Name of data file upload.

    Returns:
        pd.DataFrame: A DataFrame containing the transaction data.
    """
    if file_name.lower().endswith('.csv'):
        return pd.read_csv(file_name)
    elif file_name.lower().endswith(('.xls', '.xlsx')):
        return pd.read_excel(file_name)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """ Prepare data for analysis. Assumes the csv
        or xlsx file has the following columns: InvoiceNo, StockCode,
        Description, and Quantity.

    Args:
        df (pd.DataFrame): DataFrame containing transaction data

    Returns:
        pd.DataFrame: A DataFrame with missing rows and credits dropped.
    """
    targets = ['invoice', 'quantity', 'description', 'code']
    for target in targets:
        in_cols = df.columns.str.contains(target, case=False).sum()
        if not in_cols:
            raise ValueError(f'DataFrame is missing a {target} column.')
    df = df.dropna(axis=0, subset=['InvoiceNo'])
    df['InvoiceNo'] = df['InvoiceNo'].astype(str)
    df = df[~df['InvoiceNo'].str.contains('C')]
    return df


def encode_data(datapoint: int) -> int:
    """ One hot encode the purchase quantity of items

    Args:
        datapoint (int): The purchase quantity of a given item

    Returns:
        int: 0 for non positive quantities. 1 otherwise
    """
    if datapoint <= 0:
        return 0
    else:
        return 1


# TODO use the example from the mlxtend documentation
def generate_demo_data() -> pd.DataFrame:
    """Create data from the mlxtend examples

    Returns:
        pd.DataFrame: A one hot encoded dataframe
    """
    dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
           ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
           ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],
           ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],
           ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]
    te = TransactionEncoder()
    te_ary = te.fit(dataset).transform(dataset)
    return pd.DataFrame(te_ary, columns=te.columns_)


def generate_retail_data() -> pd.DataFrame:
    """Create one hot encoded retail data

    Args:
        file_name (str): Name of retail data file e.g. OnlineRetail.xlsx

    Returns:
        pd.DataFrame: A one hot encoded DataFrame of retail items
    """
    df = read_input_data('OnlineRetail.xlsx')
    new_df = prepare_data(df)
    market_basket = new_df[new_df['Country'] == "United Kingdom"].groupby(
        ['InvoiceNo', 'Description'])['Quantity']
    market_basket = market_basket.sum().unstack().reset_index().fillna(0).\
        set_index('InvoiceNo')
    market_basket = market_basket.applymap(encode_data)
    market_basket.drop('POSTAGE', inplace=True, axis=1)
    return market_basket


def main():
    market_basket = generate_retail_data
    itemsets = apriori(market_basket, min_support=0.03, use_colnames=True)
    rules = association_rules(
        itemsets,
        metric='lift',
        min_threshold=1
    )
    # visualize.plot_heatmap(rules)
    visualize.draw_graph(rules, 14)


if __name__ == '__main__':
    one_hot_df = generate_demo_data()
    frequent_itemsets = fpgrowth(one_hot_df,
                                 min_support=0.6,
                                 use_colnames=True)
    rules = association_rules(frequent_itemsets,
                              metric="confidence",
                              min_threshold=0.7)
    rules = association_rules(frequent_itemsets,
                              metric="lift",
                              min_threshold=1.2)
    visualize.draw_graph(rules, 5)
