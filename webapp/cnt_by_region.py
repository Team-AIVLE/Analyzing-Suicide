import re
import numpy as np
import pandas as pd
from region import REGION

def get_regexp(cities):
    return f"({'|'.join(cities)})"

def get_region(text):
    for key in REGION.keys():
        if re.findall(get_regexp(REGION[key]), text):
            return key
    return np.nan

def locate_region(data):
    data['region'] = data['text'].apply(lambda x: get_region(x))
    return data

def preprocessing(data):
    data['date'] = pd.to_datetime(data['date'])

    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data = locate_region(data)
    return data

def get_data_by_region(data):
    data_with_region = data[['region', 'year', 'month', 'text']].dropna().groupby(by=['region', 'month', 'year'], as_index=False).count()
    data_with_region['date'] = list(map(lambda x: f"{x[0]}-{x[1]}", zip(data_with_region['year'], data_with_region['month'])))
    data_with_region['date'] = pd.to_datetime(data_with_region['date'], format="%Y-%m")
    data_with_region.sort_values(by=['date'], inplace=True)
    return data_with_region

def date_to_string(x):
    return f"{x.year}"[-2:] + f"-%02d" % (x.month)
    
def get_cnt_by_region(data):
    print("get_cnt_by_region ", len(data))
    proc_data = preprocessing(data)
    data_with_region = get_data_by_region(proc_data)

    x_ticks = data_with_region[['date']].drop_duplicates(ignore_index=True)['date'].tolist()
    regions = data_with_region['region'].unique()
    
    date_df = pd.DataFrame(x_ticks, columns=['date'])
    counts = []
    for r in regions:
        data_by_r = pd.merge(date_df, data_with_region[data_with_region['region'] == r], on='date', how='outer')[['date', 'region', 'text']]
        data_by_r['text'] = data_by_r['text'].fillna(0)

        counts += [data_by_r['text'].tolist()]

    assert len(x_ticks) == len(counts[0]) and len(regions) == len(counts)        
    return list(map(date_to_string, x_ticks)), regions, counts