import dateutil
import pandas as pd

"""
    判断逻辑：逐条判断标记
    1.取一条记录，找出时间，金额，备注
    2.若金额为正，筛选出前后一小时内金额为负的记录，反之，相似
    3.从筛选出的记录里找出与当前备注一样的记录
    4.若最后筛选出的df记录数>=1,该条流水无效

    """


def exclude_same_in_out(df):
    df['nameOnOppositeCard'].fillna("', inplace=True")
    df['remark'].fillna("', inplace=True")
    """
    :param df: 网银流水df
    :param item_lst: 排除项列表
    :return: keep_df, drop_df
    """
    """
    前后一小时内，remark列或者nameOnOppositeCard列中进项账户与出项账户不能为同一主体。
    在该时间内，如果进项账户与出项账户为同一主体，则进项流水不算入有效流水。
    注意：
    1 若remark为空, 对remark不做判断。
    2 若nameOnOppositeCard为空, 对nameOnOppositeCard不做判断。
    """
    df['transDate'] = pd.to_datetime(df['transDate'])
    keep_row_lst = []
    drop_row_lst = []
    print('当前有效df一共有【%s】行' % df.shape[0])

    for index, row in df.iterrows():
        id = row['id']
        is_valid = 1
        name_on_oppsite = row['nameOnOppositeCard']
        # 逐条判断
        time = row['transDate']

        amout_money = row['amountMoney']
        remark = row['remark']
        description = row['description']

        if remark == "" and name_on_oppsite == "":
            pass
        else:
            if amout_money > 0:
                select_df = df[df['amountMoney'] < 0]
            else:
                select_df = df[df['amountMoney'] > 0]
            # 前后一小时
            start_time = time - dateutil.relativedelta.relativedelta(hours=1)
            end_time = time + dateutil.relativedelta.relativedelta(hours=1)
            #
            tmp_df = select_df[(select_df['transDate'] >= start_time) & (select_df['transDate'] <= end_time)]
            if tmp_df.shape[0] >= 1:
                if remark != "":
                    tmp_df1 = tmp_df[tmp_df['remark'] == remark]
                    if tmp_df1.shape[0] >= 1:
                        is_valid = 0
                if name_on_oppsite != "":
                    tmp_df2 = tmp_df[tmp_df['nameOnOppositeCard'] == name_on_oppsite]
                    if tmp_df2.shape[0] >= 1:
                        is_valid = 0

        if is_valid == 0:
            drop_row_lst.append(row)
        else:
            keep_row_lst.append(row)

    keep_df = pd.DataFrame(keep_row_lst)
    drop_df = pd.DataFrame(drop_row_lst)
    return keep_df, drop_df
