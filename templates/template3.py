# -*-coding:utf-8-*-
# sql_templete

# clickhouse+native://<admin>:<admin>@<192.168.8.50>:<19000>/<default>[?options…]clickhouse://{username}:{password}@{hostname}:{port}/{database}



# 多个公司issues 的发起
######################################

# 需要更改的参数
owner = "pytorch"
repo = "pytorch"
# 邮箱后缀用，分割 如 ['huawei.com','fb.com']
email_domain_list = ['huawei.com', 'fb.com']
######################################




arg1 = ""
arg2 = ""
arg3 = ""
for i, v in enumerate(email_domain_list) :

    if i == len(email_domain_list)-1:
        arg1 += f" splitByChar('@', commit__author__email)[2] = '{v}' "
        arg2 += f" \'{v.split('.')[-2]}\'"
        arg3 += f" final_company_inferred_from_company = '{v.split('.')[-2]}'"
    else:
        arg1 += f" splitByChar('@', commit__author__email)[2] = '{v}' or"
        arg2 += f" splitByChar('@', commit__author__email)[2] = '{v}', \'{v.split('.')[-2]}\',"
        arg3 += f" final_company_inferred_from_company = '{v.split('.')[-2]}' or"


if len(email_domain_list) != 1:
    arg2 = f"multiIf({arg2})"
# print(arg1)
# print(arg2)

sql_tplt = f"""
select company, count() as issues_create_count
from (select id, b.company
      from (select * from github_issues where search_key__owner = '{owner}' and search_key__repo = '{repo}' and pull_request__url = '') as a global
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
                                                                         from (select author__id as id, company, count()
                                                                               from (select author__id,
                                                                                            {arg2} as company
                                                                                     from github_commits
                                                                                     where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                                                                                       and author__id != 0
                                                                                       and ({arg1}))
                                                                               group by author__id, company
                                                                               order by id, count() desc)
                                                                         limit 1 by id))) as b on a.user__id = b.id)
group by company
order by issues_create_count desc;
"""
print(sql_tplt)
