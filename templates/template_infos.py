from .template1 import generate as DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT_GENERATOR


class TemplateNotFound(Exception):
    pass


# 每个公司有多少开发者参与贡献 模板
DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT = {
    "template_id": 0, "label": "各公司参与项目的开发者人数", "name": "DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT",
    "param_list": [{
        "name": "owner", "description": "项目组织",
    }, {
        "name": "repo", "description": "项目代码库",
    }, {
        "name": "email_domain_list", "description": "Email后缀（json数组）",
    }, {

    }

    ],
}

TEMPLATES = [DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT]

TEMPLATE_GENERATORS = {
    0: DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT_GENERATOR
}


def template_info_list():
    return [DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT]


def get_template_label(template_id):
    for template in TEMPLATES:
        if template['template_id'] == template_id:
            return template['label']

    # Handle the emtpy label outside
    return ""


def generate_sql(template_id, params):
    if template_id not in TEMPLATE_GENERATORS:
        raise TemplateNotFound()

    generator = TEMPLATE_GENERATORS[template_id]
    return generator(**params)

