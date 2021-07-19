import requests
import re
from tqdm.auto import tqdm
import pickle 
import pandas as pd
from gensim import corpora, models
from gensim.utils import simple_preprocess
from sklearn.feature_extraction.text import TfidfVectorizer
from pymystem3 import Mystem
from bs4 import BeautifulSoup
from flask import Flask,  render_template, request
from sklearn.metrics.pairwise import linear_kernel

app = Flask(__name__)


@app.route('/')
def hello():

    return render_template('index.html', title='Home')



def cleaner():
    with open('data.pickle', 'rb') as f:
        data_new = pickle.load(f)

    randomitems = ['«', '--', ',', '#' ,'-', '&', '@', '...',  '!', '?', '/', '%', 'br', '\n', '$', '<', '>', '\rb', '\r', '\\', 'li', 'ul', '&quot', '\uf0b7', 'b' , '.', ':', '[', ']', '+', ';', '(', ')', '•', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ' и ', ' с ', 'quot', ' этап ', ' этот ', ' что ', ' наш ', ' это ', ' или ']
    dicts  = {}
    count = 0
    main_list = []
    main_list2 = []
    dicts1  = {}
    mystem = Mystem()
    for i in tqdm(range(len(data_new))):
        k = data_new[i]
        if k['description'] != 'Not Found':
            k1 = k['id']
            text = k['description'].lower() # нижний регистр
            text = BeautifulSoup(text, "lxml").text
            text = re.sub(r'\|\|\|\|\\', r' ', text) 
            text = re.sub(r'http\S+', r'<URL>', text)
            text = re.sub(r'\r', r' ', text)
            text = re.sub(r'\n', r' ', text)
            #text = re.sub(r'[A-Za-z]', '', text)  # Убирает английские слова
            text = re.sub(r'\b\w{1,3}\b', '', text) #убирает слова меньше 3 символов
            text = re.sub(r'\n', r' ', text)
            for r in randomitems:
                text = text.replace(r, ' ')
            lemmas = mystem.lemmatize(text)
            
        dicts[k1] = ''.join(lemmas)
    return dicts #render_template('index.html', message=dicts) 

@app.route('/submit', methods=['post'])
def cosinus():
    dicts = cleaner()
    text = request.form.get('text').lower()
    
    df = pd.concat({k: pd.Series(v) for k, v in dicts.items()}).reset_index()
    df.columns = ['id_vac', 'index', 'descriptions']


    # формирование весов tf-idf
    tfidf = TfidfVectorizer()
    mx_tf = tfidf.fit_transform(df['descriptions'])
    new_entry = tfidf.transform([text])
    cosine_similarities = linear_kernel(new_entry, mx_tf).flatten()
 
    # запишем все попарные результаты сравнений
    df['cos_similarities'] = cosine_similarities
    # и отсортируем по убыванию (т.к. cos(0)=1)
    df = df.sort_values(by=['cos_similarities'], ascending=[0])
    #for index, row in df[0:10].iterrows():
    #    print( row[['id_vac','cos_similarities', 'descriptions'  ]])
    
    dictionary, bow_corpus, word_counts, di = corpus(dicts, text)


    return render_template('main.html',   tables=[df[0:10].to_html(classes='data', header="true")], message = [ dictionary, bow_corpus, word_counts, di])
    #return render_template('index.html',  message =[ dictionary, bow_corpus[:2], word_counts[:2], tables=[df[0:10].to_html(classes='data', header="true")]])


def corpus(dicts, text):
    processed_corpus  = []
    d = {}
    for key, values in dicts.items():
        processed_corpus.append(simple_preprocess(values, deacc=True))

    dictionary = corpora.Dictionary(processed_corpus)
    bow_corpus = [dictionary.doc2bow(text) for text in processed_corpus]
    
    word_counts = [[(dictionary[id], count) for id, count in line] for line in bow_corpus]
    tfidf = models.TfidfModel(bow_corpus)
    query_document = text.lower().split()
    query_bow = dictionary.doc2bow(query_document)
    sims = tfidf[query_bow]
    for document_number, score in sorted(sims, key=lambda x: x[1], reverse=True):
       
        d.fromkeys([document_number], score)

    return  dictionary , bow_corpus[:2], word_counts[:2], d





if __name__ == '__main__':
    app.run()
