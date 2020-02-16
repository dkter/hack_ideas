from flask import Flask, jsonify
from jinja2 import Environment, FileSystemLoader
import requests
from image import gen_logo

app = Flask(__name__)
env = Environment(loader=FileSystemLoader('templates/'))
gpt_2_api_url = 'https://gpt-5vmrd7cmdq-uc.a.run.app'


def get_idea_from_api():
    req = requests.post(gpt_2_api_url,
                        json={
                            'length': 100,
                            'temperature': 1.0,
                            'truncate': "\n\n"
                        })
    api_text = req.json()['text']
    return api_text


@app.route('/')
def hello_world():
    template = env.get_template('homepage.html')
    return template.render()


@app.route('/ajax/generate_idea')
def generate_idea():
    text = get_idea_from_api()
    if type(text) == list:
        title_text = text[0]
        description_text = text[1]
    else:
        title_text = text
        description_text = ""

    uri = gen_logo(title_text)
    data = {
        "title": title_text,
        "description": description_text,
        "uri": uri
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run()