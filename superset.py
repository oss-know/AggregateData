import requests


class DatasetCreatonFailed(Exception):
    def __init__(self, message):
        self.message = message


class SupersetApi:
    _singleton = None

    SECURITY_LOGIN_PATH = 'api/v1/security/login'
    SECURITY_CSRF_TOKEN_PATH = 'api/v1/security/csrf_token/'

    DATASET_PATH = 'api/v1/dataset/'

    def __init__(self, base_url, username, password, provider, refresh=True):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.provider = provider
        self.refresh = refresh
        self.superset_login_payload = {
            "username": self.username, "password": self.password, "provider": self.provider, "refresh": self.refresh,
        }
        self.json_fields = {}
        self.api_base_headers = {}

    @classmethod
    def info(cls):
        import json
        print(json.dumps(cls._singleton.json_fields, indent=2))
        print(json.dumps(cls._singleton.api_base_headers, indent=2))

    @classmethod
    def init(cls, base_url, username, password, provider, refresh=True):
        # Just create a new instance(the params might be updated, then just re-init)
        cls._singleton = SupersetApi(base_url, username, password, provider, refresh)
        cls._singleton.security_login()
        cls._singleton.get_session_and_csrf_token()

    @classmethod
    def security_login(cls):
        cls_singleton = cls._singleton
        request_url = f'{cls_singleton.base_url}/{SupersetApi.SECURITY_LOGIN_PATH}'
        response = requests.post(request_url, json=cls_singleton.superset_login_payload)
        access_token_and_refresh_token = response.json()
        cls_singleton.json_fields['access_token'] = access_token_and_refresh_token['access_token']
        if cls_singleton.refresh:
            cls_singleton.json_fields['refresh_token'] = access_token_and_refresh_token['refresh_token']
        cls_singleton.api_base_headers['Authorization'] = f'Bearer {access_token_and_refresh_token["access_token"]}'
        return response.status_code

    @classmethod
    def get_session_and_csrf_token(cls):
        req_url = f'{cls._singleton.base_url}/{SupersetApi.SECURITY_CSRF_TOKEN_PATH}'
        headers = {'Authorization': 'Bearer ' + cls._singleton.json_fields["access_token"]}

        response = requests.get(req_url, headers=headers)
        csrf_token_json = response.json()
        cookie_session = response.headers["Set-Cookie"].split("; ")[0].split("=")[1]
        cls._singleton.json_fields["cookie_session"] = cookie_session
        cls._singleton.json_fields["csrf_token"] = csrf_token_json["result"]

        if response.status_code == 200:
            cls._singleton.api_base_headers['Cookie'] = f'session={cls._singleton.json_fields["cookie_session"]}'
            cls._singleton.api_base_headers['CSRFToken'] = cls._singleton.json_fields['csrf_token']
            cls._singleton.api_base_headers['csrf_token'] = cls._singleton.json_fields['csrf_token']
            cls._singleton.api_base_headers['Accept'] = 'application/json'
        return response.status_code

    @classmethod
    def get_dataset_list(cls):
        req_url = f'{cls._singleton.base_url}/{SupersetApi.DATASET_PATH}'
        return requests.get(req_url, headers=cls._singleton.api_base_headers).json()

    @classmethod
    def create_dataset(cls, database_id, schema, table_name, sql):
        req_url = f'{cls._singleton.base_url}/{SupersetApi.DATASET_PATH}'
        payload = {
            "database": database_id,  # "external_url": "string",
            # "is_managed_externally": True,
            # "owners": [0],
            "schema": schema, "table_name": table_name, "sql": sql,
        }
        res = requests.post(req_url, headers=cls._singleton.api_base_headers, json=payload)
        if res.status_code != 201:
            raise DatasetCreatonFailed(res.text)

        return res.json()['id']
