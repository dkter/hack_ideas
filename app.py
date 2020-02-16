from flask import Flask, jsonify
from jinja2 import Environment, FileSystemLoader
import requests
from image import gen_logo

titles = set()
descriptions = set()
with open("projects.txt", encoding="utf-8", errors="ignore") as f:
    for project in f.read().split("\n\n"):
        try:
            title, desc = project.split("\n")
            titles.add(title)
            descriptions.add(desc)
        except ValueError:
            print(project)


app = Flask(__name__)
env = Environment(loader=FileSystemLoader('templates/'))
gpt_2_api_url = 'https://gpt-5vmrd7cmdq-uc.a.run.app'



def get_idea_from_api(retry=False):
    req = requests.post(gpt_2_api_url,
                        json={
                            'length': 200,
                            'temperature': 1.0,
                            #'truncate': "\n\n"
                        })
    api_text = req.json()['text']

    # filter out projects without a title
    generated = [tuple(i.split("\n"))
                 for i in api_text.split("\n\n")
                 if len(i.split("\n")) >= 2]

    for title, desc in generated:
        if title not in titles and desc not in descriptions:
            return title, desc
    else:
        for title, desc in descriptions:
            if desc not in descriptions:
                return title, desc
        else:
            return generated[0]


@app.route('/')
def hello_world():
    template = env.get_template('homepage.html')
    return template.render()


@app.route('/ajax/generate_idea')
def generate_idea():
    title_text, description_text = get_idea_from_api(False)
    print(title_text, description_text)

    uri = gen_logo(title_text)
    data = {
        "title": title_text,
        "description": description_text,
        "uri": uri
    }
    return jsonify(data)


if __name__ == '__main__':
    app.run()