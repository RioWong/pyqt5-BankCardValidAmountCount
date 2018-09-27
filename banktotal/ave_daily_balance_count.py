import pandas as pd
from pandas import date_range

ave_daily_balance_keyword_lst = ['结息', '利息', '季息']
# 生成3、6、9、12月21号到25号的字符串
ms = ["%s" % x for x in range(3, 13, 3)]
ds = ["%s" % x for x in range(21, 26)]
ave_days = ["%s%s" % (x, y) for x in ms for y in ds]


def get_month(datetime_str):
    month = datetime_str.month
    day = datetime_str.day
    month_day = "%s%s" % (month, day)
    if month_day in ave_days:
        return 1
    else:
        return 0


def ave_daily_balance_count(df):
    """
    :param df: 网银流水df
    :return: 日均存款余额
    """
    df['transDate'] = pd.to_datetime(df['transDate'])

    # print(date_lst)
    df['is_ave_day'] = df['transDate'].apply(get_month)
    df = df[df['is_ave_day'] == 1]
    # print(df)
    ave_pat = "|".join(ave_daily_balance_keyword_lst)
    df = df[df['description'].str.contains(r'%s' % ave_pat)]
    df['amountMoney'] = df['amountMoney'].apply(lambda x: -x)
    avg = df['amountMoney'].mean()
    ave_daily_balance = avg * 1100
    df_ave = pd.DataFrame([[ave_daily_balance]], columns=['日均存款余额'])
    return df_ave


if __name__ == "__main__":
    df = pd.read_excel("G:\PyQt5_Projects\网银有效流水计算\主程序\有效流水统计结果\陈晓飞_有效流水统计结果_6228480408244329673.xlsx")
    start_date = '20180321'
    date_index = date_range(start_date, periods=5, freq="D")
    print(date_index)
    df_ave = ave_daily_balance_count(df)
    print(df_ave)
