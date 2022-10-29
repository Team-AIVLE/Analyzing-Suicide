import os
import json
import pandas as pd
import firebase_admin

from glob import iglob
from os.path import join as pjoin
from datetime import date, datetime
from firebase_admin import credentials, db

class dbHandler:
    def __init__(self, config_dir, local_dir):
        
        with open(pjoin(config_dir, "config.json")) as f:
            config = json.load(f)
        try:
            # Firebase database 인증 및 앱 초기화
            config_keyfile = pjoin(config_dir, config['keyfile'])
            self.local_dir = local_dir
            self.cred = credentials.Certificate(config_keyfile)
            firebase_admin.initialize_app(self.cred,{
                'databaseURL': config['database_url']
            })
            self.dir = db.reference()
        except Exception as e:
            print(e)

    def load(self, node="id"):
        """Update Local dataset

        Returns:
            int : length of data
        """
        try:
            data = self.dir.get(node)[0]
            data_df = pd.DataFrame()
    
            indices, nicknames = [], []
            contents, keywords, urls = [], [], []
            timestamps = []
            for id in data.keys():
                indices += [id]
                nicknames += [id["nickname"]]
                contents += [id["text"]]
                keywords += [id["keywords"]]
                urls += [id["url"]]
                timestamps += [id["timestamp"]]
                
                
            data_df['id'] = indices
            data_df['nickname'] = nicknames
            data_df['text'] = contents
            data_df['keyword'] = keywords
            data_df['url'] = urls
            data_df['timestamps'] = pd.to_datetime(timestamps)
            
            
            data_df['date'] = data_df['timestamps'].apply(lambda x: x.date)
            data_df['time'] = data_df['timestamps'].apply(lambda x: x.time().strftime('%H:%M:%S'))
            
            
            df_len = len(data_df)
            
            data_df.to_csv(pjoin(self.local_dir, f"{date.today().strftime('%y%m%d-%H%M')}_{df_len}.csv"), index=False)
            return len(data_df)
        
        except (Exception) as e:
            print(e)
            return -1

    def close(self):
        pass
             
class locDBHandler:
    def __init__(self, config_path, local_dir):
        self.local_dir = local_dir
        self.cur_path = self.get_lastest_path()
        self.cur_df = pd.read_csv(self.cur_path)
        
        self.db = dbHandler(config_path, local_dir)

    def get_lastest_path(self):
        return list(iglob(pjoin(self.local_dir, "*.csv")))[-1]
    
    def get_updated_time(self):
        last_dt = self.cur_path.split(os.sep)[-1].split("_")[0]
        return datetime.strptime(last_dt, '%y%m%d-%H%M')
    
    def update_dataset(self):
        self.db.load(node="id")
        
        self.cur_path = self.get_lastest_path()
        self.cur_df = pd.read_csv(self.cur_path)
    
        return len(self.cur_df)
    
    def add_column(self, col_name, values):
        try:
            self.cur_df[col_name] = values
            self.cur_df.to_csv(self.cur_path, index=False)

        except Exception as e:
            print(e)
            pass
    

        