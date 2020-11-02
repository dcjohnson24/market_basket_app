from collections import namedtuple

import pandas as pd

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

Rules = namedtuple('Rules', ['confidence', 'lift', 'leverage'])


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
    targets = ['invoice', 'quantity', 'description']
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


def count_items_per_transaction(df: pd.DataFrame) -> pd.DataFrame:
    """ Count the number of items by InvoiceNo and Description

    Args:
        df (pd.DataFrame): DataFrame with columns
            InvoiceNo, Description, and Quantity

    Returns:
        pd.DataFrame: A one hot encoded DataFrame where the rows are
            InvoiceNos and the columns are Descriptions.
    """
    market_basket = df.groupby(
        ['InvoiceNo', 'Description'])['Quantity']
    market_basket = market_basket.sum().unstack().reset_index().fillna(0).\
        set_index('InvoiceNo')
    market_basket = market_basket.applymap(encode_data)
    return market_basket


def make_rules(
        one_hot_df: pd.DataFrame,
        min_support: float = 0.03,
        lift_thresh: float = 1,
        conf_thresh: float = 0.5,
        lev_thresh: float = 0.03) -> Rules:
    """ Make association rules DataFrames based on confidence, lift,
        and leverage

    Args:
        one_hot_df (pd.DataFrame): a one hot encoded DataFrame with
            rows as InvoiceNos and columns as Descriptions
        min_support (float, optional): The support threshold for generating
            frequent itemsets. Defaults to 0.03.
        lift_thresh (float, optional): The threshold for calculating
            lift metrics. Defaults to 1.
        conf_thresh (float, optional): The threshold for calculating
            confidence metrics. Defaults to 0.5.
        lev_thresh (float, optional): The threshold for calculating leverage
            metrics. Defaults to 0.03.

    Returns:
        Rules: Assocation rules DataFrames for confidence,
            lift, and leverage metrics.
    """
    itemsets = apriori(
        one_hot_df,
        min_support=min_support,
        use_colnames=True
    )

    rules_lift = association_rules(
            itemsets,
            metric='lift',
            min_threshold=lift_thresh
        )[['antecedents', 'consequents', 'lift']]

    rules_conf = association_rules(
        itemsets,
        metric='confidence',
        min_threshold=conf_thresh
    )[['antecedents', 'consequents', 'confidence']]

    rules_leverage = association_rules(
        itemsets,
        metric='leverage',
        min_threshold=lev_thresh
    )[['antecedents', 'consequents', 'leverage']]

    return Rules(
        confidence=rules_conf,
        lift=rules_lift,
        leverage=rules_leverage
    )


def rules_from_user_upload(df):
    df = prepare_data(df)
    one_hot_df = count_items_per_transaction(df)
    return make_rules(one_hot_df)


def run_demo() -> Rules:
    """ Calculates rules from mlxtend sample dataset

    Returns:
        Rules: DataFrames of association rules for lift, confidence,
            and leverage metrics.
    """
    dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
               ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
               ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],
               ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],
               ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]
    te = TransactionEncoder()
    te_ary = te.fit(dataset).transform(dataset)
    one_hot_df = pd.DataFrame(te_ary, columns=te.columns_)
    return make_rules(
        one_hot_df,
        min_support=0.6,
        conf_thresh=0.7,
        lift_thresh=1.2
    )


def run_retail_demo(read_rules: bool = True) -> Rules:
    """ Create association rules from Online Retail dataset
        https://pythondata.com/market-basket-analysis-with-python-and-pandas/
    Args:
        read_rules (bool, optional): Read association rules from file.
        Generates them otherwise. Defaults to True.

    Returns:
        Rules: DataFrames of association rules for lift, confidence,
            and leverage metrics.
    """
    if read_rules:
        xl = pd.ExcelFile('AssociationRules.xlsx')
        dfs = {sh: xl.parse(sh) for sh in xl.sheet_names}
        for key, val in dfs.items():
            for name in ['antecedents', 'consequents']:
                dfs[key][name] = val[name].apply(lambda x: eval(x))
        rules = Rules(
            confidence=dfs['confidence'][[
                'antecedents',
                'consequents',
                'confidence']],
            lift=dfs['lift'][['antecedents', 'consequents', 'lift']],
            leverage=dfs['leverage'][[
                'antecedents',
                'consequents',
                'leverage']]
        )
    else:
        df = read_input_data('OnlineRetail.xlsx')
        new_df = prepare_data(df)
        uk_df = new_df[new_df['Country'] == "United Kingdom"]
        market_basket = count_items_per_transaction(uk_df)
        market_basket.drop('POSTAGE', inplace=True, axis=1)
        rules = make_rules(market_basket)

    return rules
