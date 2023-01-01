from flask import Flask, render_template, request, redirect, url_for
import json
import itertools
from application_inverted_index import __idf__index, json_parser, temp_parse
from collections import OrderedDict
import math

merged_inverted_index = {}
no_of_articles = 1
app = Flask(__name__)
flag = True


@app.route('/')
def index():
    global flag
    return render_template('indexing.html', __condition__=flag)


@app.route("/searching-page")
def searching_page():
    return render_template('Search-Page.html')


@app.route("/searching", methods=['POST'])
def search():
    global merged_inverted_index
    temp = merged_inverted_index
    merged_inverted_index = merged_inverted_index[1]
    query = temp_parse(request.form['query'])
    query = list(set(query))
    print(query)
    _query_result = {}
    try:
        if len(query) > 1:
            query = [merged_inverted_index[x] for x in query if x in merged_inverted_index.keys()]
            for i in query:
                for url, index in i.items():
                    if url not in _query_result:
                        _query_result[url] = 0
                    _query_result[url] += index
            _query_result = dict(OrderedDict(sorted(_query_result.items(), key=lambda x: x[1], reverse=True)))
            query = _query_result
        else:
            query = merged_inverted_index[query[0]]
    except Exception as e:
        print(e)
        query = {"No Results": [0]}
    print(len(query))
    query = dict(itertools.islice(query.items(), 0, 10))
    query = list(query.keys())
    merged_inverted_index = temp
    return render_template("Search-Page.html", search_results=query)


@app.route("/InvertedCreation", methods=["POST"])
def inverted_creation():
    global flag, merged_inverted_index
    flag = False
    print("Inverted Index Loading Started")
    open_file = open("output_test.json", 'r')
    file_data = open_file.read()
    merged_inverted_index = json.loads(file_data)
    print("Inverted Indexing Preloaded")
    return redirect(url_for('index'))


def inverse__idf__index(doc_dict, no_of_docs):
    temp_ = len(doc_dict) + 1
    for key, value in doc_dict.items():
        for key_, value_ in value.items():
            value[key_] = value_ / math.log(no_of_docs / temp_)
    return doc_dict


@app.route("/DynamicContentAddition", methods=["POST"])
def dynamic_content_addition():
    global merged_inverted_index
    no_of_articles = merged_inverted_index[0]
    merged_inverted_index = merged_inverted_index[1]
    merged_inverted_index = inverse__idf__index(merged_inverted_index, no_of_articles)
    path3 = request.form['path']
    unique_tokens, doc_dict = json_parser(path3)
    merged_inverted_index = inverse__idf__index(merged_inverted_index, no_of_articles)
    no_of_articles += len(doc_dict)
    inverted_indexing = {}
    for unique_token in unique_tokens:
        inverted_indexing[unique_token] = {}
    for doc_id, tokens in doc_dict.items():
        for word, pos_list in tokens.items():
            inverted_indexing[word][doc_id] = pos_list
    indexes = [inverted_indexing, merged_inverted_index]
    merged_index = {}
    for inv_index in indexes:
        for token, docs_ in inv_index.items():
            if token not in merged_index:
                merged_index[token] = {}
            merged_index[token].update(docs_)
    for key, value in merged_index.items():
        merged_index[key] = __idf__index(value, no_of_articles)
    merged_inverted_index = (no_of_articles, merged_index)
    with open('.\\output_test.json', 'w', encoding='utf-8') as fx:
        json.dump(merged_inverted_index, fx)
    print("Done Writing")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
