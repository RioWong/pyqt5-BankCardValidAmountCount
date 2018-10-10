"""remark、nameOnOppositeCard以及transAddr 中，
将含关键字客户名、配偶名、客户公司名、客户公司股东姓名、或指定的客户亲属姓名 的记录标记为无效流水"""


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
    drop_df = df[df['tmp_col'].str.contains(exclude_words)]
    keep_df = df[~df['tmp_col'].str.contains(exclude_words)]
    del keep_df['tmp_col']
    del drop_df['tmp_col']
    return keep_df, drop_df
