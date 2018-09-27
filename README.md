# BankCardValidAmountCount
根据银行提供的网银流水记录文件（excel格式）计算其有效流水，以用于评估其收入。
## 网银流水有效流水计算规则

1排除同进同出
前后一小时内，remark列或者nameOnOppositeCard列中进项账户与出项账户不能为同一主体。在该时间内，如果进项账户与出项账户为同一主体，则进项流水不算入有效流水。
注意：
1 若remark为空, 对remark不做判断。
2 若nameOnOppositeCard为空, 对nameOnOppositeCard不做判断。

2排除借贷
需要排除的关键词：['借款', '贷款', '冲正', '消费退货', '放款', '透支回补', '钱生钱C', '退款', ‘赔款’,‘和融通’, ‘微粒贷’, ‘借呗’, ‘冲账’, “海科融通”,”和融” ，“陆金所”]。
排除remark、nameOnOppositeCard、description及transAddr中含有以上关键词的记录，标记为无效流水
3排除同名转账
remark、nameOnOppositeCard以及transAddr 中，将含关键字“客户名/配偶名/客户公司名/客户公司股东姓名 |指定客户亲属姓名”字样标记为无效流水
4 排除所有支出项（正值为支出）
将amountMoney中所有正值标记为无效流水

5支付宝/微信流水处理
将被标记为无效流水的Description、remark、nameOnOppositeCard以及transAddr中含“支付宝转账提现/微信零钱提现”的全部标记为有效流水。
6 按月计算收入总和
7 日均存款余额
每季度（3/6/9/12）21日-25日，“description”列中含“结息”、“利息”，“季息” 字样，且金额小于0，将四个季度结息金额算平均数后乘以1100，得出结果为日均存款余额
## 程序打开界面
