from . import COMPANY_ISSUES_IN_PROJECT, COMPANY_COMMITS_IN_PROJECT, DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT, \
    COMPANY_ISSUE_REPLIES_IN_PROJECT, COMPANY_PR_REVIEW_COMMENT_COUNT_IN_PROJECT, COMPANY_PR_APPROVE_COUNT_IN_REPO, \
    COMPANY_PR_IN_PROJECT, COMPANY_CONTRIBUTION_BY_DIR, COMPANY_CONTRIBUTION_BY_SPECIFIED_DIR


class TemplateNotFound(Exception):
    pass


TEMPLATE_INFO_LIST = [
    COMPANY_ISSUES_IN_PROJECT.TEMPLATE_INFO,
    COMPANY_COMMITS_IN_PROJECT.TEMPLATE_INFO,
    DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT.TEMPLATE_INFO,
    COMPANY_ISSUE_REPLIES_IN_PROJECT.TEMPLATE_INFO,
    COMPANY_PR_REVIEW_COMMENT_COUNT_IN_PROJECT.TEMPLATE_INFO,
    COMPANY_PR_APPROVE_COUNT_IN_REPO.TEMPLATE_INFO,
    COMPANY_CONTRIBUTION_BY_DIR.TEMPLATE_INFO,
    COMPANY_CONTRIBUTION_BY_SPECIFIED_DIR.TEMPLATE_INFO,
    COMPANY_PR_IN_PROJECT.TEMPLATE_INFO,

]

TEMPLATES_MAP = {
    COMPANY_ISSUES_IN_PROJECT.ID: COMPANY_ISSUES_IN_PROJECT.TEMPLATE,
    COMPANY_COMMITS_IN_PROJECT.ID: COMPANY_COMMITS_IN_PROJECT.TEMPLATE,
    DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT.ID: DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT.TEMPLATE,
    COMPANY_ISSUE_REPLIES_IN_PROJECT.ID: COMPANY_ISSUE_REPLIES_IN_PROJECT.TEMPLATE,
    COMPANY_PR_REVIEW_COMMENT_COUNT_IN_PROJECT.ID: COMPANY_PR_REVIEW_COMMENT_COUNT_IN_PROJECT.TEMPLATE,
    COMPANY_PR_APPROVE_COUNT_IN_REPO.ID: COMPANY_PR_APPROVE_COUNT_IN_REPO.TEMPLATE,
    COMPANY_CONTRIBUTION_BY_DIR.ID: COMPANY_CONTRIBUTION_BY_DIR.TEMPLATE,
    COMPANY_CONTRIBUTION_BY_SPECIFIED_DIR.ID: COMPANY_CONTRIBUTION_BY_SPECIFIED_DIR.TEMPLATE,
    COMPANY_PR_IN_PROJECT.ID: COMPANY_PR_IN_PROJECT.TEMPLATE,
}


def template_info_list():
    return TEMPLATE_INFO_LIST


def get_template_label(template_id):
    if template_id not in TEMPLATES_MAP:
        return ''
    return TEMPLATES_MAP[template_id]['label']


def generate_sql(template_id, params):
    if template_id not in TEMPLATES_MAP:
        raise TemplateNotFound()

    generator = TEMPLATES_MAP[template_id]['generator']
    return generator(**params)
