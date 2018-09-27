# 导入python 自带库

# 导入自定义模块
from Mainwindow.Mainwindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog
from banktotal.StyleFrameBankStatementsTotal import BankStatementsTotal
import images
import os

class BankStatementsTotal_main(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(BankStatementsTotal_main, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("网银有效流水计算工具_by_soaringsoul")
        icon2 = QtGui.QIcon(':/icon2/soaringsoul.jpg')
        self.setWindowIcon(icon2)
        qss = open(os.getcwd() + '/Mainwindow/Mainwindow.qss').read()
        self.setStyleSheet(qss)

        self.init_app()

    def setBrowerPath(self):
        file_path = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.xlsx , *.xls)')
        print(file_path)
        self.lineEdit_filepath.setText(file_path[0])

    def init_app(self):
        self.file_path = self.lineEdit_filepath.text()
        self.client_name = self.LineEdit_clientname.text()
        self.spouse_name = self.LineEdit_spouse.text()
        self.parents_name = self.LineEdit_parents.text()
        self.relatives_name = self.LineEdit_relatives.text()
        self.company_name = self.LineEdit_companyname.text()


    # 定义按下 开始抓取 按钮后的操作
    @pyqtSlot()
    def on_pushButton_count_clicked(self):
        self.textBrowser.clear()
        self.init_app()
        if self.file_path in ["杨过", ""]:
            self.file_path = "%s网银流水查询.xls" % self.client_name
            self.error_message("【Warn】当前网银流水excel路径为空，默认使用:【%s网银流水查询.xls】" % self.client_name)
        client_info = """以下是你输入的客户信息：
        客户姓名：{0}
        配偶姓名：{1}
        父母姓名：{2}
        亲属姓名：{3}
        公司名：{4}
        网银流水excel路径：{5}
        """.format(self.client_name, self.spouse_name, self.parents_name, self.relatives_name, self.company_name,
                   self.file_path)
        self.count_signal_display(client_info)
        self.count()

    @pyqtSlot()
    def on_pushButton_clear_clicked(self):
        item_lst = [self.LineEdit_clientname, self.LineEdit_spouse, self.LineEdit_parents, self.LineEdit_relatives,
                    self.LineEdit_companyname, self.lineEdit_filepath, self.textBrowser]
        for item in item_lst:
            item.clear()

    @pyqtSlot()
    def on_pushButton_clicked(self):
        self.setBrowerPath()

    def count(self):
        try:
            self.bank_count = BankStatementsTotal(self.file_path, self.client_name, self.spouse_name, self.parents_name,
                                                  self.relatives_name,
                                                  self.company_name)
            self.bank_count.count_signal.connect(self.count_signal_display)
            self.bank_count.start()
        except Exception as e:
            print(e)

    def count_signal_display(self, log_info):
        self.textBrowser.append(log_info)

    def error_message(self, error_info):
        self.textBrowser.setText(error_info)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    bank_counter = BankStatementsTotal_main()
    bank_counter.show()
    sys.exit(app.exec_())
