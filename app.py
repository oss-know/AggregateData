import os
from random import randint

from flask import Flask
from flask import request
from flask_cors import CORS

from superset import SupersetApi
from templates.template_infos import template_info_list, get_template_label, generate_sql, TemplateNotFound

SUPERSET_SERVER = os.environ.get('SUPERSET_SERVER', 'http://localhost:8088')
SUPERSET_USERNAME = os.environ.get('SUPERSET_USERNAME', 'admin')
SUPERSET_PASSWORD = os.environ.get('SUPERSET_PASSWORD', 'admin')
SUPERSET_PROVIDER = os.environ.get('SUPERSET_PROVIDER', 'db')

SupersetApi.init(SUPERSET_SERVER, SUPERSET_USERNAME, SUPERSET_PASSWORD, SUPERSET_PROVIDER, False)
SupersetApi.info()

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

ESSENTIAL_KEYS_CREATE_DATASET = ['template_id', 'params', 'database_id', 'schema']


@app.route('/api/dataset', methods=['POST'])
def create_dataset():  # put application's code here
    req_json = request.json
    for essential_key in ESSENTIAL_KEYS_CREATE_DATASET:
        if essential_key not in req_json:
            return {"error_msg": "Missing essential params"}, 400

    template_id = req_json['template_id']
    params = req_json['params']
    database_id = req_json['database_id']
    schema = req_json['schema']

    template_label = get_template_label(template_id)
    if not template_label:
        return {"message": "template not found"}, 400
    table_name = f'{template_label}{randint(0, 10000)}'  # TODO more prefix/suffix?

    try:
        sql = generate_sql(template_id, params)
        dataset_id = SupersetApi.create_dataset(database_id, schema, table_name, sql)
        return {"dataset_id": dataset_id}, 200
    except TemplateNotFound as e:
        return {"message": "template not found"}, 400


@app.route('/api/datasets')
def list_datasets():
    return SupersetApi.get_dataset_list()


@app.route('/api/templates', methods=['GET'])
def list_templates():
    return template_info_list()


if __name__ == '__main__':
    app.run()
