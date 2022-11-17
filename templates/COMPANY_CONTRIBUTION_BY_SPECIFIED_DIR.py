# -*-coding:utf-8-*-
# sql_templete

# clickhouse+native://<admin>:<admin>@<192.168.8.50>:<19000>/<default>[?options…]clickhouse://{username}:{password}@{
# hostname}:{port}/{database}

# 包括二级目录目录的各公司分布，头部友商


######################################

# 需要更改的参数
# owner = "pytorch"
# repo = "pytorch"
# # 邮箱后缀用，分割 如 ['huawei.com','fb.com']
# email_domain_list = ['huawei.com', 'fb.com']
# # 请添加目录层级（阿拉伯数字且数字大于等于2）
# dir_level = 2
# # 请添加目录层级结构(例：torch/csrc/jit/  要求层级结构和前方所填目录层级数量一致)
# dir_list = ['torch/csrc/jit/', 'torch/src/test']


######################################


def generate(owner, repo, email_domain_list, dir_level, dir_list):
    arg1 = ""
    arg2 = ""
    arg3 = ""
    arg5 = ""
    for i, v in enumerate(email_domain_list):

        if i == len(email_domain_list) - 1:
            arg1 += f" splitByChar('@', commit__author__email)[2] = '{v}' "
            arg2 += f" \'{v.split('.')[-2]}\'"
            arg5 += f" \'{v.split('.')[-2]}\'"
            arg3 += f" final_company_inferred_from_company = '{v.split('.')[-2]}'"
        else:
            arg1 += f" splitByChar('@', commit__author__email)[2] = '{v}' or"
            arg2 += f" splitByChar('@', commit__author__email)[2] = '{v}', \'{v.split('.')[-2]}\',"
            arg3 += f" final_company_inferred_from_company = '{v.split('.')[-2]}' or"
            arg5 += f"\'{v.split('.')[-2]}\',"

    arg6 = ""
    for i, v in enumerate(dir_list):

        if i == len(email_domain_list) - 1:
            arg6 += f"{v}"
        else:
            arg6 += f"{v},"

    if len(email_domain_list) != 1:
        arg2 = f"multiIf({arg2})"

    return f"""select *
    from (
             select search_key__owner, search_key__repo, in_dir, company, month, count() as company_alter_file_count
             from (select search_key__owner,
                          search_key__repo,
                          in_dir,
                          toYYYYMM(authored_date) as month,
                          {arg2}       as company
                   from gits_dir_label
                   where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                     and ({arg1})
                     and length(splitByChar('/', in_dir)) = {int(dir_level) + 1}
    
    
                   union all
                   select search_key__owner, search_key__repo, in_dir, month, company
                   from (select a.search_key__owner, a.search_key__repo, a.in_dir, a.month, b.author__id as id
                         from (select search_key__owner,
                                      search_key__repo,
                                      in_dir,
                                      toYYYYMM(authored_date) as month,
                                      author_email
                               from gits_dir_label
                               where search_key__owner = '{owner}' and search_key__repo = '{repo}'
                                 and not ({arg1})
                                 and length(splitByChar('/', in_dir)) = {int(dir_level) + 1}) as a global
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
                                                            where search_key__owner = '{owner}' and search_key__repo 
                                                            = '{repo}'
                                                              and author__id != 0
                                                            group by author__id)
                                                      where author__id global not in (select id
                                                                                      from (select author__id as id, 
                                                                                      company, count()
                                                                                            from (select author__id,
                                                                                                         {arg2} as 
                                                                                                         company
                                                                                                  from github_commits
                                                                                                  where 
                                                                                                  search_key__owner = 
                                                                                                  '{owner}' and 
                                                                                                  search_key__repo = 
                                                                                                  '{repo}'
                                                                                                    and author__id != 0
                                                                                                    and ({arg1}))
                                                                                            group by author__id, company
                                                                                            order by id, count() desc)
                                                                                      limit 1 by id))) as b on a.id = 
                                                                                      b.id)
             group by search_key__owner, search_key__repo, in_dir, company, month
             )
    where search_key__owner = '{owner}' and search_key__repo = '{repo}'
      and company global in ({arg5}) 
      and in_dir global in
          ({arg6}) order by in_dir,month;
    """


######################################
ID = 'COMPANY_CONTRIBUTION_BY_SPECIFIED_DIR'
TEMPLATE_INFO = {
    "label": "各公司在项目中的贡献（按照指定目录划分）",
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
        },
        {
            "name": "dir_level", "description": '目录层级（阿拉伯数字且数字大于等于2）'
        },
        {
            "name": "dir_list", "description": '指定目录，json数组，如：["torch/csrc/jit/", "torch/src/test"]'
        }
    ],
}
TEMPLATE = TEMPLATE_INFO.copy()
TEMPLATE['generator'] = generate
