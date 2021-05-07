import sys
import os
from os.path import dirname, abspath, join

sys.path.append(os.pardir)
path = dirname(dirname(abspath(__file__)))
sys.path.append(join(path, 'model'))

import pandas as pd

from model.apriori import rules_from_user_upload
from . import celery


@celery.task
def _rules_from_user_upload(df_json: str, metric: str) -> str:
    df = pd.read_json(df_json)
    rules = rules_from_user_upload(df)
    return rules._asdict()[metric].to_json()
