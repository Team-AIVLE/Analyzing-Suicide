import json, re
import pandas as pd
import seaborn as sns
from glob import iglob
from os.path import join as pjoin

from flask import *
from io import BytesIO, StringIO
from flask import Flask, send_file, render_template, make_response
from flask import jsonify, request

from ast import literal_eval
from functools import wraps, update_wrapper, reduce
from datetime import datetime, timedelta
from collections import Counter, OrderedDict

from log import Logger
from utilities.colors import get_palette
from db_handler import locDBHandler
from graph import build_highlighted_graph
from cnt_by_region import get_cnt_by_region, get_total_cnt_by_region
from word_embedding import WordModel

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = "static"

DATA_DIR = pjoin("static", "data")
MODEL_DIR = pjoin("static", "model")
CONFIG_PATH = "config/"
loc_db = locDBHandler(CONFIG_PATH, DATA_DIR)

logger = Logger('api-log', './log/')

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
    

def load_keyword():
    temp = pd.read_csv(pjoin(DATA_DIR, "221027-0000_528.csv"), converters={
        "noum" : literal_eval
    })
    keywords = temp['noum'].tolist()
    keywords = reduce(lambda x, y: x + y, keywords)
    
    keywords = Counter(keywords)
    keywords = dict(OrderedDict(keywords.most_common()))
    
    return keywords

@app.route('/api/keyword_weights', methods=['GET'])
def get_keyword_weights():
    keywords = load_keyword()
    
    labels = [k for k in keywords.keys()]
    weight = [k for k in keywords.values()]
    words = [{"key" : l, "weight" : w} for l, w in zip(labels, weight)]
    
    return jsonify({'words': words})


@app.route('/api/keyword_counts', methods=['GET'])
def get_keyword_counts():
    keywords = load_keyword()
    labels = [k for k in keywords.keys()][0:10]
    values = [k for k in keywords.values()][0:10]
    
    max_values = (max(values) // 100 + 1) * 100
    colors = get_palette(n_colors=len(labels))
    
    return jsonify({'labels': labels, 'values' : values, 'max_values' : max_values, 'colors' : colors})


@app.route('/api/keyword_counts_by_region', methods=['GET'])
def get_keyword_counts_by_region():
    labels, values = get_total_cnt_by_region(loc_db.cur_df)
    
    max_values = (max(values) // 10 + 1) * 10
    colors = get_palette(n_colors=len(labels), palette="viridis")
    
    return jsonify({'labels': labels, 'values' : values, 'max_values' : max_values, 'colors' : colors})


@app.route('/api/data_len_by_region', methods=['GET'])
def get_data_len_by_region():
    """지역별 유해게시물 발생 통계
    Returns:
        x_ticks (list): 시간 x축
        regions (list): 지역
        counts (list): 지역별 유해 게시물 발생 횟수
    """
    x_ticks, regions, counts = get_cnt_by_region(loc_db.cur_df)
    colors = get_palette(n_colors=len(regions))
    
    return jsonify({'x_ticks': x_ticks, 'regions' : regions, 'counts' : counts, 'colors' : colors})


def load_data_with_related_keyword():
    word_model = WordModel(data=loc_db.cur_df, model_dir=MODEL_DIR)
    
    data = pd.DataFrame()
    data['category'] = ['동반자 모집', '판매/활용', '구체적 정보 제공', '판매/활용', '판매/활용']
    data['id'] = [0, 1, 2, 3, 4]

    data['word'] = ['ㄷㅂㅈㅅ','ㅈㅍㄷ', 'ㅂㄱㅌ','ㅅㅁㅈ','ㅅㅌㄴㅅ' ]
    data['neighbors'] = [word_model.get_similar_words('ㄷㅂㅈㅅ'),
                         word_model.get_similar_words('ㅈㅍㄷ'),
                         word_model.get_similar_words('ㅂㄱㅌ'),
                         word_model.get_similar_words('ㅅㅁㅈ'),
                         word_model.get_similar_words('ㅅㅌㄴㅅ')
                         ]
    return data

@app.route('/api/related_sale', methods=['GET'])
def get_related_words_with_sale():
    
    data = load_data_with_related_keyword()
    
    nodes, edges = build_highlighted_graph(data, keywords=['ㅈㅍㄷ', 'ㅅㅁㅈ', 'ㅅㅌㄴㅅ'], logger=logger)    
    return jsonify({'nodes': nodes, 'edges' : edges})


@app.route('/api/related_info', methods=['GET'])
def get_related_words_with_info():
    
    data = load_data_with_related_keyword()
    
    nodes, edges = build_highlighted_graph(data, keywords=['ㅂㄱㅌ'], logger=logger)
    return jsonify({'nodes': nodes, 'edges' : edges})


@app.route('/api/related_recruit', methods=['GET'])
def get_related_words_with_recruit():
    
    data = load_data_with_related_keyword()

    nodes, edges = build_highlighted_graph(data, keywords=['ㄷㅂㅈㅅ'], logger=logger)
    return jsonify({'nodes': nodes, 'edges' : edges})


def time_formatting(x):
    h, m, s = map(int, x.split(":"))
    return "%02d:%02d:%02d" % (h, m, s)

def del_nickname(x):
    return re.sub("@[a-zA-Z0-9_-]+", " ", x).strip()
    
    
@app.route('/api/raw_data', methods=['GET'])
def get_raw_data():    
    elements = loc_db.cur_df[['text', 'url', 'date', 'time', 'search_keyword']]
    elements['time'] = elements['time'].apply(time_formatting)
    elements['text'] = elements['text'].apply(del_nickname)
    
    elements['Timestamp'] = list(map(lambda x: f"{x[0]} {x[1]}", zip(elements['date'], elements['time'])))
    elements.drop(columns=['date', 'time'], inplace=True)
    
    elements.rename(columns={
        'text' : "Text",
        'url' : "URL",
        'search_keyword' : "Keyword",
    }, inplace=True)

    elements_json = elements.to_json(orient='records')
    
    return jsonify({'data': json.loads(elements_json)})


if __name__ == '__main__':
    app.run(debug=True, 
         host='0.0.0.0', 
         port=5000,
         threaded=True)
  