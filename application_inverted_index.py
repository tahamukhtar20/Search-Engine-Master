from concurrent.futures import ProcessPoolExecutor
import math
import json
import os
import datetime
import itertools
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from nltk.stem.snowball import SnowballStemmer
import pandas as pd
import re
from collections import OrderedDict

punctuations = re.compile(r'[^\w\s]')
stop_words = set(stopwords.words('english'))
tokenizer = WordPunctTokenizer()
stemmer = SnowballStemmer('english')
temp = 0


def temp_parse(x):
    x = tokenizer.tokenize(punctuations.sub('', x))
    x = [stemmer.stem(word) for word in x if word.lower() not in stop_words]
    return x


def conversion(x):
    temp = {}
    temp_var = 0
    try:
        temp_var = 1 / (len(x) + 1)
    except Exception as e:
        pass
    for i in range(len(x)):
        if x[i] not in temp:
            temp[x[i]] = temp_var
        else:
            temp[x[i]] += temp_var
    return temp


def json_parser(path1):
    with open(path1, 'r') as f:
        df = pd.DataFrame(json.load(f))
    df['content'] = df['content'].apply(temp_parse)
    unique_tokens = list(set(itertools.chain.from_iterable(df["content"].tolist())))
    df["content"] = df["content"].apply(conversion)
    doc_dict = {row['url']: row['content'] for row in df.to_dict(orient='records')}
    return unique_tokens, doc_dict


def inverted_index(path2):
    unique_tokens, doc_dict = json_parser(path2)
    inverted_indexing = {}
    for unique_token in unique_tokens:
        inverted_indexing[unique_token] = {}
    for doc_id, tokens in doc_dict.items():
        for word, tf_score in tokens.items():
            inverted_indexing[word][doc_id] = tf_score
    return inverted_indexing


def create_inverted_index(path3):
    indexes = []
    if len(os.listdir(path3)) < 6:
        for file in os.listdir(path3):
            indexes.append(inverted_index(path3 + file))
    else:
        with ProcessPoolExecutor() as executor:
            indexes = list(executor.map(inverted_index, (path3 + x for x in os.listdir(path3))))
        print("Inverted Indexing Done")
    merged_index = {}
    for inv_index in indexes:
        for token, docs_ in inv_index.items():
            if token not in merged_index:
                merged_index[token] = {}
            merged_index[token].update(docs_)
    return merged_index


def articles_count(path3):
    with ProcessPoolExecutor() as executor:
        __templist_ = list(executor.map(read_file, (path3 + x for x in os.listdir(path))))
    _noof_docs = sum(__templist_)
    print("Total Number of Documents: ", _noof_docs)
    return _noof_docs


def read_file(path):
    with open(path, "r", encoding="utf-8") as f1:
        no_of_docs = len(json.load(f1))
    return no_of_docs


def __idf__index(doc_dict, no_of_docs):
    temp_ = no_of_docs / (len(doc_dict) + 1)
    # print(temp_)
    temp1 = math.log(temp_)
    for key_, value_ in doc_dict.items():
        doc_dict[key_] = value_ * temp1
    doc_dict = OrderedDict(sorted(doc_dict.items(), key=lambda x: x[1], reverse=True))
    return doc_dict


if __name__ == '__main__':
    path = ".\\minidataset\\"
    x1 = datetime.datetime.now()
    index = create_inverted_index(path)
    no_of_articles = articles_count(path)
    for key, value in index.items():
        index[key] = __idf__index(value, no_of_articles)
    final_index = (no_of_articles, index)
    print("Inverted Indexing Done")
    with open('.\\output1_test.json', 'w', encoding='utf-8') as fx:
        json.dump(final_index, fx)
    print(f"Time taken: {datetime.datetime.now() - x1}")
