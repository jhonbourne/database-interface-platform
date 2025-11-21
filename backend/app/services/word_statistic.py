import jieba
from repositories.mysqlhelper import MySqlHelper
from repositories.database_info import *

import os
current_dir = os.path.dirname(os.path.abspath(__file__))
stopwords_file_name = 'hit_stopwords.txt'
stopwords_file = os.path.join(current_dir, stopwords_file_name)
with open(stopwords_file, 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()
def filter_stopwords(word_list):
    return [word for word in word_list if word not in stopwords]

doubantopmovies_noise_words = [
    '|','/','主演','导演','：','...',':'
]

class WordStatistic:
    def __init__(self, name, path=''):
        user, pwd = authority_check()

        self.name = name
        self.columns = get_word_statistic_columns(self.name)
        print(self.columns)

        self.data = []
        with MySqlHelper(user=user, password=pwd,
                    database=get_database4src(path)) as dial:
            data_, _ = dial.select(name, column_names=self.columns)
            self.data.append(data_)

        # Extract all string values from possibly multilevel nested lists/tuples
        self.texts = []
        def _extract_strings(obj):
            if isinstance(obj, str):
                self.texts.append(obj)
            elif isinstance(obj, (list, tuple, set)):
                for item in obj:
                    _extract_strings(item)

        _extract_strings(self.data)

    def word_cleaning(self, words, raw_texts):
        cleaned_texts = []
        if 'doubantopmovies' in self.name:
            '''
            words: list of list
            raw_texts: list of str

            Discard noise words and parts of full names.
            TODO?: avoid discarding parts of full title (words seperate by blank).
            '''
            noise = set(doubantopmovies_noise_words)
            # Find full names in the original texts that contain spaces or middle dot
            import re
            # (English)+ +(English)
            eng_pattern = re.compile(r'[A-Za-z]+(?:[\s][A-Za-z]+)+')
            # (Chinese)+·+(Chinese)
            chi_pattern = re.compile(r'[\u4e00-\u9fff]+(?:[·][\u4e00-\u9fff]+)+')
            
            for i,t in enumerate(self.texts):
                full_names = []
                if not isinstance(t, str):
                    continue
                for m in eng_pattern.findall(t):
                    full_names.append(m.strip())
                for m in chi_pattern.findall(t):
                    full_names.append(m.strip())
                
                for wd in words[i]:
                    token = wd.strip()
                    if not token:
                        continue
                    if token in noise:
                        continue
                    discard = False
                    # discard token if it's a part of a detected full name
                    for name in full_names:
                        if token in name and len(name) > len(token):
                            discard = True
                            break
                    if not discard:
                        cleaned_texts.append(token)
                cleaned_texts.extend(full_names)
  
        else:
            for seg in words:
                for wd in seg:
                    token = wd.strip()
                    if token:
                        cleaned_texts.append(token)

        # Cleaning process for any text
        cleaned_texts = filter_stopwords(cleaned_texts)

        return cleaned_texts

    def word_cut(self):
        words = []
        for t in self.texts:
            wds = jieba.lcut_for_search(t)
            words.append(wds)
        print('Done cutting words.')
        print(words)
        self.words = self.word_cleaning(words,self.texts)
        print(f'Total {len(self.words)} words after cleaning.')

    def word_count(self):
        self.word_cut()
        word_freq = {}
        for word in self.words:
            if word.strip():
                word_freq[word] = word_freq.get(word, 0) + 1
        return word_freq
    

if __name__ == '__main__':
    ws = WordStatistic(name='doubantopmovies_2025_nov_11')
    freq = ws.word_count()
    print(freq)
