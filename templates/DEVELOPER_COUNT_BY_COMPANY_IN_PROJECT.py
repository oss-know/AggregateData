# -*-coding:utf-8-*-


# 每个公司有多少开发者参与贡献 模板


######################################

# 需要更改的参数
# owner = "pytorch"
# repo = "pytorch"
# # 邮箱后缀用，分割 如 ['huawei.com','fb.com']
# email_domain_list = ['huawei.com','fb.com']
######################################


def generate(owner, repo, email_domain_list):
    arg1 = ""
    arg2 = ""
    arg3 = ""
    for i, v in enumerate(email_domain_list):

        if i == len(email_domain_list) - 1:
            arg1 += f" splitByChar('@', commit__author__email)[2] = '{v}' "
            arg2 += f" \'{v.split('.')[-2]}\'"
            arg3 += f" final_company_inferred_from_company = '{v.split('.')[-2]}'"
        else:
            arg1 += f" splitByChar('@', commit__author__email)[2] = '{v}' or"
            arg2 += f" splitByChar('@', commit__author__email)[2] = '{v}', \'{v.split('.')[-2]}\',"
            arg3 += f" final_company_inferred_from_company = '{v.split('.')[-2]}' or"

    if len(email_domain_list) != 1:
        arg2 = f"multiIf({arg2})"

    sql_tplt = f"""
    select company, count() as developer_count
    from (select id, company
          from (select author__id as id, company, count()
                from (select author__id,
                             {arg2} as company
                      from github_commits
                      where search_key__owner = '{owner}'
                        and search_key__repo = '{repo}'
                        and author__id != 0
                        and ({arg1}))
                group by author__id, company
                order by id, count() desc)
          limit 1 by id
    
          union all
          select id, company
          from (select id, final_company_inferred_from_company as company
                from github_profile
                where {arg3}
                group by id, final_company_inferred_from_company)
          where id global in (select *
                              from (select author__id
                                    from github_commits
                                    where search_key__owner = '{owner}' and search_key__repo = '{repo}' and 
                                    author__id != 0
                                    group by author__id)
                              where author__id global not in (select id
                                                              from (select author__id as id, company, count()
                                                                    from (select author__id,
                                                                                 {arg2} as company
                                                                          from github_commits
                                                                          where search_key__owner = '{owner}'
                                                                            and search_key__repo = '{repo}'
                                                                            and author__id != 0
                                                                            and ({arg1}))
                                                                    group by author__id, company
                                                                    order by id, count() desc)
                                                              limit 1 by id)))
    group by company
    order by count() desc
    """
    return sql_tplt


######################################
ID = 'DEVELOPER_COUNT_BY_COMPANY_IN_PROJECT'
TEMPLATE_INFO = {
    "label": "各公司参与项目的开发者人数",
    "template_id": ID,
    "params": [
        {
            "name": "owner", "description": "项目组织",
        },
        {
            "name": "repo", "description": "项目代码库",
        },
        {
            "name": "email_domain_list", "description": "Email后缀（json数组）",
        }
    ],
}
TEMPLATE = TEMPLATE_INFO.copy()
TEMPLATE['generator'] = generate
