import os

from flask import Flask
from flask import request

from templates.template_infos import template_info_list
from superset import SupersetApi

SUPERSET_SERVER = os.environ.get('SUPERSET_SERVER', 'http://localhost:8088')
SUPERSET_USERNAME = os.environ.get('SUPERSET_USERNAME', 'admin')
SUPERSET_PASSWORD = os.environ.get('SUPERSET_PASSWORD', 'admin')
SUPERSET_PROVIDER = os.environ.get('SUPERSET_PROVIDER', 'db')

SupersetApi.init(SUPERSET_SERVER, SUPERSET_USERNAME, SUPERSET_PASSWORD, SUPERSET_PROVIDER, False)
SupersetApi._singleton.info()

app = Flask(__name__)


# @app.route('/')
# def hello_world():  # put application's code here
#     return 'Hello World!'


@app.route('/api/dataset', methods=['POST'])
def create_dataset():  # put application's code here
    req_json = request.json
    if 'template_id' not in req_json or 'params' not in req_json:
        return {"error_msg": "Missing essential params"}, 400
    # TODO Generate sql from template
    result = SupersetApi.create_dataset(0, 'default', 'select count() from gits')
    print(result)
    return 'Hello World!'


@app.route('/api/datasets')
def list_datasets():
    return SupersetApi.get_dataset_list()


@app.route('/api/templates', methods=['GET'])
def list_templates():
    return template_info_list()


if __name__ == '__main__':
    app.run()
