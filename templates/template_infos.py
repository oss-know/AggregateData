from .template1 import generate as DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT_GENERATOR

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

TEMPLATE_GENERATORS = {
    "DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT": DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT_GENERATOR
}


def template_info_list():
    return [DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT]
