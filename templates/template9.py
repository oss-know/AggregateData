# -*-coding:utf-8-*-
# sql_templete

# clickhouse+native://<admin>:<admin>@<192.168.8.50>:<19000>/<default>[?options…]clickhouse://{username}:{password}@{hostname}:{port}/{database}

# 包括二级目录目录的各公司分布，头部友商
######################################

# 需要更改的参数
owner = "pytorch"
repo = "pytorch"
# 邮箱后缀用，分割 如 ['huawei.com','fb.com']
email_domain_list = ['huawei.com','fb.com']
# 请添加目录层级（阿拉伯数字且数字大于等于2）
dir_level = 2
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

sql_tplt = f"""select search_key__owner, search_key__repo, in_dir, company, count() as company_alter_file_count
from (select search_key__owner,
             search_key__repo,
             in_dir,
             {arg2} as company
      from gits_dir_label
      where search_key__owner = '{owner}' and search_key__repo = '{repo}'
        and ({arg1})
        and length(splitByChar('/', in_dir)) = {int(dir_level)+1}


      union all
      select search_key__owner, search_key__repo, in_dir, company
      from (select a.search_key__owner, a.search_key__repo, a.in_dir, b.author__id as id
            from (select search_key__owner, search_key__repo, in_dir, author_email
                  from gits_dir_label
                  where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                    and not ({arg1})
                    and length(splitByChar('/', in_dir)) = {int(dir_level)+1}) as a global
                     join (select commit__author__email, author__id
                           from github_commits
                           where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                             and author__id != 0
                           group by commit__author__email, author__id) as b
                          on a.author_email = b.commit__author__email) as a global
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
                          where search_key__owner = '{owner}' and search_key__repo = '{repo}' and author__id != 0
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
                                                    limit 1 by id))) as b on a.id = b.id)
group by search_key__owner, search_key__repo, in_dir, company
"""
print(sql_tplt)
