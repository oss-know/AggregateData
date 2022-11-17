# -*-coding:utf-8-*-
# sql_templete

# clickhouse+native://<admin>:<admin>@<192.168.8.50>:<19000>/<default>[?options…]clickhouse://{username}:{password}@{
# hostname}:{port}/{database}

# pr 的发起
######################################

# 需要更改的参数
# owner = "pytorch"
# repo = "pytorch"
# # 邮箱后缀用，分割 如 ['huawei.com','fb.com']
# email_domain_list = ['huawei.com', 'fb.com']


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

    # sql4 = input("请添加目录层级（阿拉伯数字且数字大于等于2）：")
    if len(email_domain_list) != 1:
        arg2 = f"multiIf({arg2})"

    return f"""select company, count() as pr_create_count
    from (select id, b.company
          from (select * from github_pull_requests where search_key__owner = '{owner}' and search_key__repo = '{repo}') 
          as a global
                   join (select id, company
                         from (select author__id as id, company, count()
                               from (select author__id,
                                            {arg2} as company
                                     from github_commits
                                     where search_key__owner = '{owner}' and search_key__repo = '{repo}'
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
                                                   where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                                                     and author__id != 0
                                                   group by author__id)
                                             where author__id global not in (select id
                                                                             from (select author__id as id, company, 
                                                                             count()
                                                                                   from (select author__id,
                                                                                                {arg2} as company
                                                                                         from github_commits
                                                                                         where search_key__owner = '
    {owner}' and search_key__repo = '{repo}'
                                                                                           and author__id != 0
                                                                                           and ({arg1}))
                                                                                   group by author__id, company
                                                                                   order by id, count() desc)
                                                                             limit 1 by id))) as b on a.user__id = b.id)
    group by company
    order by pr_create_count desc;
    """


######################################
ID = 'COMPANY_PR_IN_PROJECT'
TEMPLATE_INFO = {
    "label": "公司在项目中发起的PR",
    "template_id": ID,
    "params": [
        {
            "name": "owner", "description": "项目组织",
        },
        {
            "name": "repo", "description": "项目代码库",
        },
        {
            "name": "email_domain_list", "description": 'Email后缀（json数组，如["huawei.com", "google.com"]）',
        },
    ],
}
TEMPLATE = TEMPLATE_INFO.copy()
TEMPLATE['generator'] = generate
