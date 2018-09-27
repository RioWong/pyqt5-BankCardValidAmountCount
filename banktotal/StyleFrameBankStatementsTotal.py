import os

import numpy as np
import pandas as pd
from PyQt5 import QtCore

from .ave_daily_balance_count import ave_daily_balance_count
##################################################
from .exceptions_mark import exceptions_mark
from .exclude_loan import exclude_loan
from .exclude_relatives import exclude_relatives
from .exclude_same_in_out import exclude_same_in_out
from .styledf2excel import styledf2excel

##################################################


class DfProcess(QtCore.QThread):
    def __init__(self, file_path):
        super(DfProcess, self).__init__()
        self.file_path = file_path

    def main(self):
        try:
            df = pd.read_excel(r'%s' % self.file_path)
            df = df.drop_duplicates()
            df = df[df['cardType'] == "借记卡"]
            row_num = df.shape[0]
            df['sort_id'] = [x for x in range(row_num)]
            df_dict = {}
            for card_num, group in df.groupby(by=['fullCardNums']):
                group.reset_index(drop=True, inplace=True)
                df_dict[card_num] = group
            return df_dict
        except Exception as e:
            error = """读取excel文件出错！检查输入的网银流水excel路径是否正确！当前错误详情：%s
                   """ % e
            print(error)
            return None


class BankStatementsTotal(QtCore.QThread):
    count_signal = QtCore.pyqtSignal(str)

    def __init__(self, file_path, client_name, spouse_name, parents_name, relatives_name, company_name):
        super(BankStatementsTotal, self).__init__()
        self.file_path = file_path
        self.client_name = client_name
        self.spouse_name = spouse_name
        self.parents_name = parents_name
        self.relatives_name = relatives_name
        self.company_name = company_name
        self.file_path = file_path

    def run(self):
        df_dict = self.get_df_dict()
        if df_dict != None:
            for cardnum, df in df_dict.items():
                self.count_signal.emit("【状态】正在计算卡号为【%s】的有效流水" % cardnum)
                self.etl(df)
            self.count_signal.emit("*" * 50)
            self.count_signal.emit("【状态】有效流水计算结束!可以关闭本程序了")
            self.count_signal.emit("*" * 50)
        else:
            self.count_signal.emit("【warn】无流水数据！，检查你输入的excel路径是否正确！")

    def etl(self, df):
        print('开始etl')
        df['nameOnOppositeCard'].fillna('', inplace=True)
        df['remark'].fillna('', inplace=True)
        df['description'].fillna('', inplace=True)
        df['transAddr'].fillna('', inplace=True)
        df['fullCardNums'] = df['fullCardNums'].astype(str)
        card_num_lst = list(set(list(df['fullCardNums'])))
        self.card_num = card_num_lst[0]
        rows_count = df.shape[0]
        # 添加新列：是否有效流水，1为有效，0为无效，默认为0
        df['是否有效流水'] = 0
        # 添加新列：唯一编号，保证输出的流水最后保持原顺序
        df['transDate'] = pd.to_datetime(df['transDate'])
        ######################################################################################
        ######################################################################################
        self.count_signal.emit("*" * 50)
        # 开始定义计算规则
        # 1 排除同进同出
        self.count_signal.emit("【状态】开始对同进同出的的流水记录进行标记!")
        keep_df, drop_df1 = exclude_same_in_out(df)

        # 2 排除借贷
        self.count_signal.emit("【状态】开始对含有借贷关键词的流水记录进行标记!")
        keep_df, drop_df2 = exclude_loan(keep_df)
        # 3 排除同名转账
        self.count_signal.emit("【状态】开始对**同名转账**流水记录进行标记!")
        items_lst = [x.strip() for x in
                     [self.client_name, self.spouse_name, self.parents_name, self.parents_name, self.company_name,
                      self.relatives_name] if x != ""]
        relatives_lst = []
        for items in items_lst:
            item_lst = [x for x in items.split("|") if x != ""]
            if item_lst:
                relatives_lst.extend(item_lst)
        keep_df, drop_df3 = exclude_relatives(keep_df, relatives_lst)
        # 4 排除流水中所有支出 ，即排除所有流水为正值的记录
        self.count_signal.emit("【状态】开始对**支出类型**流水记录进行标记!")
        drop_df4 = keep_df[keep_df['amountMoney'] >= 0]
        keep_df = keep_df[keep_df['amountMoney'] < 0]
        # 5 特殊情况处理：支付宝/微信流水处理
        self.count_signal.emit("【状态】开始对**支付宝转账提现和微信零钱提现**流水记录进行标记!")
        drop_df = pd.concat([drop_df1, drop_df2, drop_df3, drop_df4])
        drop_df['是否有效流水'] = 0
        drop_df.drop_duplicates(inplace=True)
        keep_df_add, drop_df5 = exceptions_mark(drop_df)
        self.count_signal.emit("*" * 50)
        ######################################################################################
        """
        对经过1、2、3、4步骤处理标记的有效流水记录和无效流水记录进行汇总
        """
        keep_df = pd.concat([keep_df, keep_df_add])
        drop_df = drop_df5
        keep_df['是否有效流水'] = 1
        keep_df.drop_duplicates(inplace=True)
        drop_df['是否有效流水'] = 0
        drop_df.drop_duplicates(inplace=True)
        ######################################################################################

        # ## 有效流水按月份统计
        df_invalid = drop_df
        df_valid = keep_df
        clean_rows_count = df_valid.shape[0] + df_invalid.shape[0]
        check_result = """【状态】当前卡号下的流水数据一共有：%s行；标记是否有效流水后一共有：%s行；
        """ % (rows_count, clean_rows_count)
        print(check_result)
        self.count_signal.emit(check_result)

        # 按月份汇总归纳有效流水
        df_all = pd.concat([df_valid, df_invalid])
        df_all.sort_values(by=['sort_id'], ascending=True, inplace=True)

        # 按月计算收入总和

        def count_3sig(money):

            s = df_valid['amountMoney']
            s = s.apply(lambda x: -x)
            u = s.mean()
            std = s.std()
            money = -money
            y = (money - u) / std
            if y > u + 3 * std:
                return '异常'
            else:
                return '无异常'

        ######################################################################################

        # 使用3sig法则标记异常流水，目前来看没有用处

        self.count_signal.emit("【状态】开始标记异常流水")
        if df_valid.shape[0] >= 1:
            df_valid['异常有效流水标注'] = df_valid['amountMoney'].apply(count_3sig)
            df_invalid['异常有效流水标注'] = ''
        else:
            df_invalid['异常有效流水标注'] = ''
        ######################################################################################

        # 计算各月份有效流水总和
        if df_valid.shape[0] >= 1:
            df_mon = df_valid.copy()
            df_mon.set_index('transDate', inplace=True)
            df_mon = df_mon.to_period('M')
            df_mon['amountMoney'] = df_mon['amountMoney'].apply(lambda x: -x)
            # df_mon['月份'] = df_mon['transDate']
            df_pivot = pd.pivot_table(df_mon, index=['transDate'], values=['amountMoney'], aggfunc=np.sum)
            df_pivot["月份"] = df_pivot.index.strftime("%Y-%m")
            df_pivot = pd.DataFrame(df_pivot, columns=['月份', 'amountMoney'])
            df_pivot.set_index(keys='月份', inplace=True)
        else:
            df_pivot = pd.DataFrame()
        self.count_signal.emit("【状态】计算各月份有效流水总和完成！")
        # 计算日均存款余额
        ######################################################################################

        df_all = pd.concat([df_valid, df_invalid])
        df_ave = ave_daily_balance_count(df_all)
        self.count_signal.emit("【状态】计算日均存款余额完成！")
        ######################################################################################

        ######################################################################################

        # 使用styleframe 美化excel后 写入到本地
        # 指定outfile_path：输出的文件地址
        self.count_signal.emit("【状态】正在美化excel结果并写入到本地！请耐心等待！")
        out_dir_path = os.path.join(os.getcwd(), "有效流水统计结果")
        if not os.path.exists(out_dir_path):
            os.mkdir(out_dir_path)
        outfile_path = os.path.join(out_dir_path, '%s_有效流水统计结果_%s.xlsx' % (self.client_name, self.card_num))

        # 按原始流水文件排序
        df_all.sort_values(by=['sort_id'], ascending=True, inplace=True)
        del df_all['sort_id']
        df_client_info = self.get_client_info()

        new_col = ['是否有效流水', 'transDate', 'amountMoney', 'description',
                   'remark', 'oppositeCardNo', 'nameOnOppositeCard', 'cardType', 'fullCardNums', 'id',
                   'shoppingsheetId', 'billId',
                   'relationId', 'bankName', 'billMonth', 'cardNum', 'category',
                   'postDate', 'currencytype', 'orderIndex',
                   'balance', 'transAddr', 'transMethod', 'transChannel', 'oppositeBank',
                   'createTime', 'lastModifyTime', '异常有效流水标注']
        # 格式化输出到excel
        df_all = pd.DataFrame(df_all, columns=new_col)
        "格式化df_all的日期列"
        df_all['transDate'] = df_all['transDate'].apply(self.datetime2str)
        "格式化各月份有效流水"
        df_pivot['月份'] = df_pivot.index
        df_pivot = pd.DataFrame(df_pivot, columns=['月份', 'amountMoney'])
        print(df_all.shape[0], df_pivot.shape[0], df_client_info.shape[0], df_ave.shape[0])
        styledf2excel(outfile_path, df_all=df_all, df_pivot=df_pivot, df_client_info=df_client_info, df_ave=df_ave)
        self.count_signal.emit("【结果】写入完毕！，结果文件路径：%s" % outfile_path)

    def datetime2str(self, dt):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def get_df_dict(self):
        dir_path = os.getcwd()
        file_path = self.file_path
        if file_path == "":
            file_path = os.path.join(dir_path, r"%s网银流水查询.xls" % self.client_name)
        # 指定客户银行流水excel表单路径
        self.count_signal.emit("【状态】开始读取本地excel文件, 当前路径：%s" % file_path)
        self.get_df_dict = DfProcess(file_path)
        df_dict = self.get_df_dict.main()
        self.count_signal.emit("【状态】读取完毕！，开始计算有效流水")
        return df_dict

    def get_client_info(self):
        col_lst = ['客户姓名', '配偶姓名', '父母姓名', '亲属姓名', '公司名']
        values_lst = [self.client_name, self.spouse_name, self.parents_name, self.relatives_name, self.company_name]
        df = pd.DataFrame([values_lst], columns=col_lst)

        return df
