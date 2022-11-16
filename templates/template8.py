# -*-coding:utf-8-*-
# sql_templete

# clickhouse+native://<admin>:<admin>@<192.168.8.50>:<19000>/<default>[?options…]clickhouse://{username}:{password}@{hostname}:{port}/{database}

# --每个公司有多少开发者参与贡献
######################################

# 需要更改的参数
owner = "pytorch"
repo = "pytorch"
# 邮箱后缀用，分割 如 ['huawei.com','fb.com']
email_domain_list = ['huawei.com','fb.com']
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

sql_tplt = f"""select company,
       count()
           developer_count
from (select id, company
      from (
               select author__id      as id,
                      {arg2} as company
               from github_commits
               where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                 and author__id != 0
                 and ({arg1})
               group by company, author__id
               union all
               select id, company
               from (select id, final_company_inferred_from_company as company
                     from github_profile
                     where {arg3}
                     group by id, company)
               where id global in (select author__id
                                   from github_commits
                                   where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                                     and author__id != 0
                                   group by author__id))
      group by id, company
         )
group by company
order by developer_count desc;
"""
print(sql_tplt)
