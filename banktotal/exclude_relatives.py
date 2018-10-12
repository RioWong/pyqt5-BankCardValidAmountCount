"""

1 remark、nameOnOppositeCard以及transAddr 中，
将含关键字“客户名/配偶名/客户公司名/客户公司股东姓名 |指定客户亲属姓名”字样标记为无效流水

2 description列中若含有"客户名+支付信转账"，则判定为无效流水

"""
import pandas as pd

def exclude_relatives(df, relatives_lst):
    # 如果打算对 "description"列也进行筛选，将use_descripton的值改为"是"
    use_descripton = "否"
    """
    :param df: 网银流水df
    :param relatives_lst: ['客户名', '配偶名', '客户公司名', '客户公司股东姓名', '指定的客户亲属姓名']
    :return: keep_df, drop_df
    """
    df['nameOnOppositeCard'].fillna('', inplace=True)
    df['remark'].fillna('', inplace=True)
    df['transAddr'].fillna('', inplace=True)
    df['description'].fillna('', inplace=True)
    if use_descripton == "否":
        df['tmp_col'] = df['remark'] + "|||" + df['nameOnOppositeCard'] + "|||" + df['transAddr']
    else:
        df['tmp_col'] = df['remark'] + "|||" + df['nameOnOppositeCard'] + "|||" + \
                        df['transAddr'] + "|||" + df['description']
    exclude_words = "|".join(relatives_lst)
    drop_df1 = df[df['tmp_col'].str.contains(exclude_words)]
    keep_df1 = df[~df['tmp_col'].str.contains(exclude_words)]

    # 新增规则：description列中若含有"客户名+支付宝转账"，则判定为无效流水

    pat2 = r'{name}支付宝转账'.format(name=relatives_lst[0])
    keep_df = keep_df1[~keep_df1['description'].str.contains(pat2)]
    drop_df2 = keep_df1[keep_df1['description'].str.contains(pat2)]

    drop_df = pd.concat([drop_df1, drop_df2])
    del keep_df['tmp_col']
    del drop_df['tmp_col']
    return keep_df, drop_df
