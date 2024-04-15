from bs4 import BeautifulSoup
from openai import OpenAI
from flask import Flask, request

import requests
import json
import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

code_inst = '''You are a helpful assistant. You will be provided with text from
an HTML snippet. If you identify code, you should also parse it in order to
identify which libraries are used, and which functions from each library are
called. Your output MUST be in a JSON format.'''

output_inst = '''You should provide your output in a JSON format with the
following schema:

{
    "code-text": string = the actual code if the given text contains Python
    code, otherwise None,
    "libraries": dict[] = a list where each entry represents an external
    library used in the code, and is a dictionary like: {"name": string =
    name of library, "functions": string[] = list of functions from this
    library that are called in the code snippet},
}

Do not wrap the json codes in JSON markers. Your entire response/output is going 
to consist of a single JSON object, and you will NOT wrap it within JSON md markers.

Do not output any markdown at all. YOU ONLY OUTPUT ONE JSON OBJECT with no markers. No code blocks. 

'''

app = Flask(__name__)

lib_to_docs = {
    "torch": "https://pytorch.org/docs/stable/generated/{}.html",
    "torch.nn": "https://pytorch.org/docs/stable/generated/{}.html",
    "torch.nn.functional": "https://pytorch.org/docs/stable/generated/{}.html",
    "numpy": "https://numpy.org/doc/stable/reference/generated/{}.html",
    "pandas": "https://pandas.pydata.org/docs/reference/api/{}.html",
    "sklearn": "https://scikit-learn.org/stable/modules/generated/{}.html",
    "matplotlib": "https://matplotlib.org/stable/api/_as_gen/{}.html",
    "tensorflow": "https://www.tensorflow.org/api_docs/python/{}.html",
    "keras": "https://keras.io/api/{}/",
    "scipy": "https://docs.scipy.org/doc/scipy/reference/generated/{}.html",
    "networkx": "https://networkx.org/documentation/stable/reference/generated/{}.html",
    "seaborn": "https://seaborn.pydata.org/generated/{}.html",
    "PIL": "https://pillow.readthedocs.io/en/stable/handbook/{}.html",
    "requests": "https://requests.readthedocs.io/en/master/api/{}.html",
    "flask": "https://flask.palletsprojects.com/en/2.2.x/api/{}.html",
    "django": "https://docs.djangoproject.com/en/4.1/ref/{}/",
    "sqlalchemy": "https://docs.sqlalchemy.org/en/14/genindex.html#{}",
    "boto3": "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/{}.html",
    "beautifulsoup4": "https://www.crummy.com/software/BeautifulSoup/bs4/doc/{}.html",
    "fastapi": "https://fastapi.tiangolo.com/en/genindex/#{}",
    "pyspark": "https://spark.apache.org/docs/latest/api/python/{}.html",
    "opencv-python": "https://docs.opencv.org/4.5.5/d6/d00/tutorial_py_root.html#{}",
    "pymongo": "https://pymongo.readthedocs.io/en/stable/api/{}.html"
}

pseudonyms = {
    "pd": "pandas",
    "np": "numpy",
    "cv2": "opencv-python",
    "tf": "tensorflow",
    "kt": "keras",
    "sk": "sklearn",
    "sb": "seaborn",
    "plt": "matplotlib",
    "rq": "requests",
    "bs4": "beautifulsoup4",
    "fa": "fastapi",
    "pm": "pymongo",
    "nx": "networkx",
    "sp": "scipy",
    "pl": "PIL",
    "fl": "flask",
    "dj": "django",
    "sa": "sqlalchemy",
    "b3": "boto3",
}

def get_html(url): 
    response = requests.get(url)
    html = response.text
    return html


def get_code(html): 
    soup = BeautifulSoup(html, 'html.parser')
    codeblocks = soup.find_all("pre")
    return [c.text for c in codeblocks]


def create_msg(role, content):
    '''
    role: {'system', 'user'}
    '''
    return {
        "role": role,
        "content": content
    }


def get_response(messages):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # response_format={type: "json_object"},
        messages=messages
    )

    return completion.choices[0].message.content


def parse_code(html_text):

    msgs = [create_msg('system', code_inst),
            create_msg('system', output_inst),
            create_msg('user', html_text)]

    resp = get_response(msgs)

    print(resp)

    try:
        print("Parsing as json")
        return json.loads(resp)
    except Exception as e: 
        print(e)
        return None
    # finally: 
    #     return None


def get_doc_urls(obj): 

    if not obj:
        return None

    doc_urls = []
    for d in obj['libraries']: 
        lib_name = pseudonyms[d["name"]] if d["name"] in pseudonyms else d["name"]
        docs_url = lib_to_docs[lib_name]

        for func in d["functions"]: 
            call = f'{lib_name}.{func}'
            func_url = docs_url.format(call)
            doc_urls.append(func_url)

    return doc_urls

@app.route("/get_urls", methods=["POST"])
def get_urls_from_html(): 
    html = request.json['html']
    # print(html)
    parsed = parse_code(html)
    print(parsed)
    urls = get_doc_urls(parsed)
    print(urls)
    return urls







