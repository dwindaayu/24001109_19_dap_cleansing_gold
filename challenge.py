from flask import Flask, jsonify, request
import re
import pandas as pd
import sqlite3
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

app = Flask(__name__)

def lower_text(text):
    return text.lower()                                                           # lowertext

def clean_text(text):
    text = re.sub('\n',' ',text)                                                  # Remove every '\n'
    text = re.sub('rt',' ',text)                                                  # Remove every retweet symbol
    text = re.sub('user',' ',text)                                                # Remove every username
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text)  # Remove every URL
    text = re.sub('  +', ' ', text)                                               # Remove extra spaces
    return text

def remove_unicode(text):
    text = re.sub(r'\bx[a-fA-F0-9]{2}\b', '', text) 
    text = re.sub(r'\bx([a-fA-F0-9]{2})', '', text)
    return text

def remove_nonalphanumeric(text):
    text = re.sub('[^0-9a-zA-Z]+', ' ', text) 
    return text

df = pd.read_csv(r'D:\Binar\Gold_Challenge_Dwinda\data\new_kamusalay.csv', encoding= 'latin1', header=None)
kamus_alay = df
kamus_alay_map = dict(zip(kamus_alay[0], kamus_alay[1]))
def alay_word(text):
    return ' '.join([kamus_alay_map[word] if word in kamus_alay_map else word for word in text.split(' ')])

def remove_extra_spaces(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def processed_text(text): 
    text = lower_text(text)
    text = clean_text(text)
    text = remove_unicode(text)
    text = remove_nonalphanumeric(text)
    text = alay_word(text)
    text = remove_extra_spaces(text)
    return text

def db_connection():
    conn = sqlite3.connect(r'D:\Binar\Gold_Challenge_Dwinda\challenge_text.db')     # database connection
    conn.row_factory = sqlite3.Row
    return conn

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        "title": "API Documentation for Data Processing",
        "version": "1.2.3",
        "description": "Dokumentasi API untuk Data Processing",
    },
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "docs",
            "route": "/docs.json"
        },
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)

@swag_from("docs/text_processing.yaml", methods=['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():
    text = request.form.get('text')
    cleaned_text = processed_text(text)

    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO texts (text, text_processing) VALUES(?, ?)", (text, cleaned_text))
    conn.commit()

    conn.close()

    json_response = {
        "status_code": 200,
        "description": "Teks yang sudah diproses",
        "data": cleaned_text,
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/text_processing_file.yaml", methods=['POST'])
@app.route('/text_processing_file', methods=['POST'])
def text_processing_file():
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file, encoding='latin1')
    texts = df.Tweet.to_list()
    cleaned_text2 = []
    for text in texts:
        cleaned_text2.append(processed_text(text))

    conn = db_connection()
    cursor = conn.cursor()

    for text in cleaned_text2:
        cursor.execute("INSERT INTO texts (text, text_processing) VALUES(?, ?)", (text, text))
    conn.commit()

    conn.close()

    json_response = {
        "status_code": 200,
        "description": "Teks yang sudah diproses",
        "data": cleaned_text2,
    }

    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
    app.run()
