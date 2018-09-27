exception_word_lst = ['支付宝转账提现', '微信零钱提现']


def exceptions_mark(drop_df):
    """
    :param drop_drop_df:被标记为无效流水的drop_df
    :return: keep_drop_df, new_drop_drop_df
    """
    """
    将Description、remark、nameOnOppositeCard以及transAddr中
    含【支付宝转账提现或微信零钱提现】”的全部标记为有效流水。
    """
    drop_df['nameOnOppositeCard'].fillna('', inplace=True)
    drop_df['remark'].fillna('', inplace=True)
    drop_df['description'].fillna('', inplace=True)
    drop_df['transAddr'].fillna('', inplace=True)
    exception_words = "|".join(exception_word_lst)
    drop_df['tmp_col'] = drop_df['remark'] + "|||" + drop_df['nameOnOppositeCard'] + "|||" + drop_df['transAddr'] + "|||" + drop_df[
        'description']
    # 将不含有支付宝转账提现或微信零钱提现的记录标记为无效流水
    new_drop_df = drop_df[~drop_df['tmp_col'].str.contains(exception_words)]
    # 将含有支付宝转账提现或微信零钱提现的记录标记为有效流水
    keep_df = drop_df[drop_df['tmp_col'].str.contains(exception_words)]
    del keep_df['tmp_col']
    del new_drop_df['tmp_col']
    return keep_df, new_drop_df
    return keep_df, new_drop_df
