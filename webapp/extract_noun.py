import urllib3
import json

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
        return []
    
    sents = data['return_object']['sentence']
    nouns = []
    for sent in sents:
        for m in sent['morp']:
            if m['type'].startswith(("SH", "NNG")):
                nouns += [m['lemma']]
    return nouns
