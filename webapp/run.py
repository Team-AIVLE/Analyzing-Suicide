import os
import pandas as pd
from glob import iglob
from os.path import join as pjoin

from flask import *
from io import BytesIO, StringIO
from flask import Flask, send_file, render_template, make_response
from flask import jsonify, request

from functools import wraps, update_wrapper
from datetime import date, datetime, timedelta
from db_handler import dbHandler, locDBHandler
from extract_noun import get_nouns

import numpy as np
from ast import literal_eval
import urllib3
from collections import Counter, OrderedDict

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = "static"

DATA_DIR = pjoin("static", "data")
CONFIG_PATH = "config/"
loc_db = locDBHandler(CONFIG_PATH, DATA_DIR)

# Remove Cache
def nocache(view):
  @wraps(view)
  def no_cache(*args, **kwargs):
    response = make_response(view(*args, **kwargs))
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response      
  return update_wrapper(no_cache, view)


@app.route('/', methods=['GET', 'POST'])
def root():
    # Count
    data_len = load_data()
    set_region()
    
    return render_template("index.html", data_len=data_len)


@app.route('/charts', methods=['GET', 'POST'])
def charts():
    return render_template("charts.html")


@app.route('/tables', methods=['GET', 'POST'])
def tables():
    return render_template("tables.html")


def load_data():
    last_dt = loc_db.get_updated_time()
    cur_dt = datetime.today()
    
    if cur_dt - last_dt >= timedelta(hours=1):
        length = loc_db.update_dataset()
    
    print(length)
    return length
    

def get_region(text):
    return None

def set_region():
    if 'region' in loc_db.cur_df.columns: return
    
    regions = []
    for i, d in loc_db.cur_df.iterrows():
        regions += [get_region(d['text'])]
    
    loc_db.add_column(col_name="region", values=regions)
    return

def load_keyword():
    
    keywords=loc_db.cur_df['search_keyword'].value_counts()
    keywords=keywords.astype(np.int32)
    keywords=dict(keywords)
    keywords={k:int(v) for k,v in keywords.items()}
    text = []
    text = loc_db.cur_df['text'].values
    morp = []
    for i in range(len(loc_db.cur_df)):
        noun = get_nouns(text[i])
        morp += noun
        
    keywords=Counter(morp)
    x=OrderedDict(keywords.most_common())
    keywords=dict(x)
    keywords={key:value for key, value in keywords.items() if value >= 10}
    
    return keywords

@app.route('/api/keyword_weights', methods=['GET'])
def get_keyword_weights():
    keywords = load_keyword()
    
    labels = list(map(lambda x: x[0], keywords.items()))
    weight = list(map(lambda x: x[-1], keywords.items()))
    words = [{"key" : l, "weight" : w} for l, w in zip(labels, weight)]
    
    return jsonify({'words': words})


@app.route('/api/keyword_counts', methods=['GET'])
def get_keyword_counts():
    keywords = load_keyword()
    labels = list(map(lambda x: x[0], keywords.items()))[0:10]
    values = list(map(lambda x: x[-1], keywords.items()))[0:10]
    
    max_values = (max(values) // 500 + 1) * 500
    return jsonify({'labels': labels, 'values' : values, 'max_values' : max_values})


@app.route('/api/data_len_by_region', methods=['GET'])
def get_data_len_by_region():
    """지역별 유해게시물 발생 통계
    Returns:
        x_ticks (list): 시간 x축
        regions (list): 지역
        counts (list): 지역별 유해 게시물 발생 횟수
    """
    # 유해게시물 많이 발생하는 지역 순으로, 20개 지역만 반환
    
    x_ticks = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    regions = ["대전", "청주", "공주"]
    counts = [[0, 0, 1, 4, 6, 11, 15, 20, 11, 9, 5, 8],
              [10, 15, 10, 5, 5, 3, 2, 24, 19, 18, 15, 9],
              [0, 1, 1, 2, 1, 1, 3, 2, 1, 4, 5, 11]]

    return jsonify({'x_ticks': x_ticks, 'regions' : regions, 'counts' : counts})
    
    
    
if __name__ == '__main__':
    app.run(debug=True, 
         host='0.0.0.0', 
         port=5000, 
         threaded=True)
  