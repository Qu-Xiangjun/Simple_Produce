from Simple_Produce import *
"""
停车场计费demo
停车一小时内收费5元
停车一小时以上，六小时以下，超出1小时部分每小时收费3元
停车六小时以上，超出六小时的计费规则为每小时1元
事实：
    a:停车时间 float
    b:基本收费时间界限 1h
    c:基本收费单位 5 yuan 
    d:二级收费时间界限 6h
    e:二级收费单位 3 yuan
    f:三级收费单位 1 yuan
    g:应缴费用
规则：
    if a<=b then g = c
    if (a>b)&(a<=d) then g = c+(3*(a-b))
    if (a>d) then g = c+3*(d-b)+(a-d)
"""
Fact = {
    'b' : 1,
    'c' : 5,
    'd' : 6,
    'e' : 3,
    'f' : 1,    
}
Rule = {
    'a<=b' : 'g = c',
    '(a>b)&(a<=d)' : 'g = c+(3*(a-b))',
    '(a>d)' : 'g = c+3*(d-b)+(a-d)'
}
m = MyProduce(Fact,Rule)
m.addFact({'a':3})
m.RUN()
for line in m.getInfo():
    print(line)
m.StoreInfo("demoProduce.txt")