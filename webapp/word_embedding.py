
import re

from glob import iglob
from os.path import join as pjoin
from soynlp.tokenizer import RegexTokenizer
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors


class WordModel:
    def __init__(self, data=None, model_dir=None):
        if not list(iglob(pjoin(model_dir, "*.model"))):
            tokenizer = RegexTokenizer()
            text = data['text'].apply(self.preprocessing)
            tokens = text.apply(tokenizer.tokenize)
            
            self.model = Word2Vec(tokens, min_count=10)
            self.model.save(pjoin(model_dir, 'word2vec.model'))

        else:
            self.model = Word2Vec.load(pjoin(model_dir, 'word2vec.model'))
        
    def get_similar_words(self, word, threshold=0.5):
        related_word = list(filter(lambda x: x[-1] >= threshold, self.model.wv.most_similar(word)))
        return list(map(lambda x: x[0], related_word))
    
    def preprocessing(self, text):
        # 개행문자 제거
        text = re.sub('\\\\n', ' ', text)
        # 한글만 남기고 모두 제거
        text = re.sub('[^가-힣ㄱ-ㅎㅏ-ㅣ]', ' ', text)
        return text