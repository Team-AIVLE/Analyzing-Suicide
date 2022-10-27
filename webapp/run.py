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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static"

DATA_DIR = pjoin("static", "data")
CONFIG_PATH = "config/config.json"
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


@app.route('/')
@nocache
def root():
    # Count
    data_len = load_data()
    set_region()
    
    
    return render_template("index.html", data_len=data_len)


def load_data():
    last_dt = loc_db.get_updated_time()
    cur_dt = datetime.today()
    
    if cur_dt - last_dt >= timedelta(hours=1):
        length = loc_db.update_dataset()
    
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
    keywords = {
        "ㄷㅂㅈㅅ" : 3333,
        "ㅈㅅㅇ" : 3145,
        "ㅂㄱㅌ" : 1564,
        "ㅊㅅㄱㄹ" : 1450,
        "끈" : 667,
        "ㅁㅌ" : 99,
        "청주" : 10
    }
    return keywords

@app.route('/api/keyword_weights', methods=['GET'])
def get_keyword_weights():
    keywords = load_keyword()
    
    labels = list(map(lambda x: x[0], keywords.items()))
    weight = [16.5, 15.5, 15, 14.5, 9.67, 6.9, 5]
    words = [{"key" : l, "weight" : w} for l, w in zip(labels, weight)]
    
    return jsonify({'words': words})


@app.route('/api/keyword_counts', methods=['GET'])
def get_keyword_counts():
    keywords = load_keyword()
    labels = list(map(lambda x: x[0], keywords.items()))
    values = list(map(lambda x: x[-1], keywords.items()))
    
    max_values = (max(values) // 1000 + 1) * 1000
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
  app.run(debug=True)
  