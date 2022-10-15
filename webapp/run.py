import urllib3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import firebase_admin
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from datetime import date, datetime, timedelta

from wordcloud import WordCloud

from functools import reduce
from collections import Counter
from os.path import join as pjoin
from firebase_admin import credentials, db
from django.shortcuts import HttpResponse, render

from flask import Flask, send_file, render_template, make_response
from flask import *
from io import BytesIO, StringIO

## remove cache 
from functools import wraps, update_wrapper
from datetime import datetime

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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static"

#Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('API_KEY_FILE')
firebase_admin.initialize_app(cred,{
    'databaseURL':'DATABASE_URL'
})

dir = db.reference()

MORP_API_URL = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"
API_KEY = ""
def get_nouns(text):
    http = urllib3.PoolManager()
    requestJson = {
        "access_key": API_KEY,
        "argument": {
            "text": text,
            "analysis_code": "morp"
        }
    }

    response = http.request(
        "POST",
        MORP_API_URL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )
    data = json.loads(str(response.data, 'utf-8'))
    if data['result'] < 0:
        print(f"Error : {data['reason']}")
        return []
    
    sents = data['return_object']['sentence']
    nouns = []
    for sent in sents:
        for m in sent['morp']:
            print(m)
            if m['type'].startswith(("SH", "NNG")):
                nouns += [m['lemma']]
    return nouns

def load_data():
    data = dir.get('id')[0]
    print(data)
    texts = ["ㄷㅂㅈㅅ 하실분 구함", "ㅈㅅㅇ 가지고 있어요", "ㄷㅂㅈㅅ 진짜 하실분만", "ㅈㅅㅇ ㅂㄱㅌ이 제일 나아요", 
             "ㄷㅂㅈㅅ 살기 싫어", "ㅈㅅㅇ 구해요", "ㅈㅅ하고 싶다"]
    
    texts = list(map(get_nouns, texts))
    
    
    # for id in data.keys():
    #     texts += [get_nouns(id["text"])]
    data_len = len(texts)
    texts = list(reduce(lambda x, y: x + y, texts))
    return data_len, '\n'.join(texts)


def update_chart(text):
    tokens = list(map(lambda x: x.split(), text.split("\n")))
    tokens = list(reduce(lambda x, y: x + y, tokens))

    tokens = Counter(tokens)
    
    chart_data = list(map(list, tokens.most_common()))
    print(chart_data)
    
    labels = list(map(lambda x: x[0], chart_data))
    data = list(map(lambda x: x[-1], chart_data))
    
    return labels, data

def update_wordcloud(text):
    # 워드 클라우드 이미지 재저장
    wcl = WordCloud(max_font_size=200, 
                    background_color='white', 
                    width=800, height=800, 
                    font_path='BMDOHYEON_ttf.ttf')
    wcl.generate(text)
    plt.imshow(wcl)

    plt.savefig(pjoin(app.config['UPLOAD_FOLDER'], "wordcloud.png"))
    return 
    
    
@app.route('/')
@nocache
def root():
    data_len, texts = load_data()
    
    labels, data = update_chart(texts)
    return render_template("index.html", wordcloud = "static/wordcloud.png", labels=labels, data=data, data_len=data_len)


if __name__ == '__main__':
  app.run(debug=True)
  