pos_black_lst = ['和融通', '海科融通', '和融', "陆金所"]
loan_word_lst = ['借款', '微粒贷', '借呗', '贷款', '冲正', '冲账', '消费退货', '放款', '透支回补', '钱生钱C', '退款',
                 '赔款']

"""排除remark、nameOnOppositeCard、description及transAddr中含有以上关键词的记录，标记为无效流水"""


def exclude_loan(df):
    """
    :param df: 网银流水df
    :return: keep_df, drop_df
    """
    df['nameOnOppositeCard'].fillna('', inplace=True)
    df['remark'].fillna('', inplace=True)
    df['description'].fillna('', inplace=True)
    df['transAddr'].fillna('', inplace=True)

    exclude_word_lst = loan_word_lst + pos_black_lst
    exclude_words = "|".join(exclude_word_lst)
    df['tmp_col'] = df['remark'] + "|||" + df['nameOnOppositeCard'] + "|||" + df['transAddr'] + "|||" + df[
        'description']
    drop_df = df[df['tmp_col'].str.contains(exclude_words)]
    keep_df = df[~df['tmp_col'].str.contains(exclude_words)]
    del keep_df['tmp_col']
    del drop_df['tmp_col']
    return keep_df, drop_df
