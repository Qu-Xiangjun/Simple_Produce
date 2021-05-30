"""
author: quxiangjun
email: quxiangjun@cqu.edu.cn
describe: 这是一个简单的产生式推理机系统类，
        通过传入dict类型的事实、规则库初始化类
        通过run函数启动推理机
        通过stop函数来暂停推理机
        通过resume函数来继续开始推理机
        通过reset函数来重置推理机
        通过getInfo来将推理过程返回
        通过storeInfo来将推理过程存储到一个文件中
        有addFact和deleteFact两种改变对应Fact值
"""
import threading


class MyProduce():
    def __init__(self, Fact=None, Rule=None):
        """
        初始化事实库和规则库，将事实库的事实申明为类中局部变量
        :param Fact: 事实库（dict) key为事实a,b,c,d...的a~z26个小写字母
        :param Rule: 规则库（dict）key为包含事实的判断表达式,形如a>b,a<c,a>0,a>13
                    右端value是对事实的运算和赋值操作语句,形如a=a+1,a = a+b(注意不支持一个运算式子里面包含逗号隔开的多个式子)
        """
        self.Fact = None
        self.mark = None
        self.Rules = None
        self.Fact2RulesLeft = None
        self.isStop = None
        self.txtStr = None

        if(Fact == None):
            Fact = {}
        if(Rule == None):
            Rule = {}
        self.Fact = Fact  # 事实库
        self.mark = {}  # 事实库使用标记，1表示可以触发，0表示已触发了
        self.Rules = Rule  # 规则库
        # 对规则库进行语法检查
        for k, v in self.Rules.items():
            if("=" not in v):
                print("[ERROR]产生式右端不存在赋值语句")
                exit(1)
        self.Fact2RulesLeft = {}  # 事实映射到可以触发的规则列表左端
        # 初始化事实的局部变量和事实映射到规则list
        for k, v in self.Fact.items():
            exec("self."+str(k)+"="+str(v))
            self.mark[str(k)] = 1
            self.Fact2RulesLeft[k] = []  # 事实映射到规则list
            for k2, v2 in self.Rules.items():
                if(k in k2):
                    self.Fact2RulesLeft[k].append(k2)

        self.isStop = False  # 是否停止
        self.txtStr = []  # 记录推理过程，其中项为存的字符串

    def RUN(self):
        """
        运行推理机
        """
        while(True):
            if(self.isStop):  # 暂停执行
                continue
            # 允许执行，未暂停
            nowFactKey = None
            # step1:找到一个没有被触发的
            for k, v in self.mark.items():
                if(v == 1):
                    nowFactKey = k
                    break
            if(nowFactKey == None):  # 当所有的事实已经执行，跳出
                break
            # step2: 标记此事实已执行
            self.mark[nowFactKey] = 0
            # step3: 找到此事实映射的产生式集合
            nowRuleLeft = self.Fact2RulesLeft.get(nowFactKey, [])  # 产生式左端列表
            # step4: 执行此产生式列表 并添加右端新产生的标记
            for itemleft in nowRuleLeft:
                # 首先执行左端判断是否可以触发
                templeft = ""
                for i in itemleft:
                    if i in "abcdefghijklmnopqrstuvwxyz":
                        # 找到了事实
                        if(self.Fact.get(i, None) == None):
                            print("[ERROR]存在未定义的事实参与计算")
                            exit(1)
                        i = "self."+i  # 添加变量的self
                    if(i == '&'):
                        i = " and "
                    if(i == '|'):
                        i = " or "
                    templeft += i
                isDo = eval(templeft)
                if(not isDo):  # 不可触发
                    continue

                # 执行可触发的产生式右边
                item = self.Rules[itemleft]
                temp = ""  # 可执行式子
                for i in item.split("=")[1]:
                    if i in "abcdefghijklmnopqrstuvwxyz":
                        # 找到了事实
                        if(self.Fact.get(i, None) == None):
                            print("[ERROR]存在未定义的事实参与计算")
                            exit(1)
                for i in item:
                    if i in "abcdefghijklmnopqrstuvwxyz":
                        # 找到了事实
                        i = "self."+i  # 添加变量的self
                    if(i == '&'):
                        i = " and "
                    if(i == '|'):
                        i = " or "
                    temp += i
                try:
                    exec(temp)  # 执行产生式
                    self.txtStr.append("Excute Rule: "+itemleft+" -> "+item)
                except:
                    print("[ERROR]执行产生式出错")
                    print("[INFO]执行的式子为：", temp)
                    exit(1)

                # 找出temp中等式左端
                leftFact = None
                for i in item.split("=")[0]:
                    if i in "abcdefghijklmnopqrstuvwxyz":
                        leftFact = i
                        break
                try:
                    # 更新Fact事实中的变量值
                    exec("self.Fact[" + "'" + leftFact +
                         "'" + "]=" + temp.split("=")[1])
                    self.mark[leftFact] = 1  # 添加右端新产生的标记
                    self.txtStr.append(
                        "Add Fact   : " + str(leftFact) + " = " + str(self.Fact[leftFact]))
                except:
                    print("[ERROR]更新Fact事实中的变量值出错")
                    print("[INFO]执行的式子为：", "self.Fact[" + "'" +
                          leftFact + "'" + "]=" + temp.split("=")[1])
                    exit(1)

    def run(self):
        """
        运行线程
        """
        th1 = threading.Thread(target=MyProduce.RUN, args=(self,))
        th1.start()
        # th1.join()

    def stop(self):
        """
        停止执行
        """
        self.isStop = True  # 暂停
        print("stop")

    def resume(self):
        """
        继续执行
        """
        self.isStop = False

    def reset(self, Fact=None, Rule=None):
        """
        重置
        :param Fact: 事实库（dict)
        :param Rule: 规则库（dict）
        """
        # 首先删除所有的事实
        for k, v in self.Fact.items():
            exec("self."+str(k)+"="+"None")
            self.mark[str(k)] = 1
        # 初始化新的事实和规则库
        if(Fact == None):
            Fact = {}
        if(Rule == None):
            Rule = {}
        self.Fact = Fact  # 事实库
        self.mark = {}  # 事实库使用标记，1表示可以触发，0表示已触发了
        for k, v in self.Fact.items():
            exec("self."+str(k)+"="+str(v))
            self.mark[str(k)] = 1
        self.isStop = False  # 是否停止

    def addFact(self, newFact):
        """
        新增Fact,可以掩盖旧的事实库中相同项
        :param newFact: 新增的事实dict
        """
        for k, v in newFact.items():
            self.Fact[k] = v
            exec("self."+str(k)+"="+str(v))
            self.mark[str(k)] = 1

    def deleteFact(self, deleteFactDict):
        """
        删除对应的Fact,即将对应的值变为None即可
        :param deleteFactDict: 删除的事实dict
        """
        for k, v in deleteFactDict.items():
            if(self.Fact.get(k, None) != None):
                exec("self."+str(k)+"="+"None")
                self.Fact[k] = None
                self.mark[str(k)] = 1

    def getInfo(self):
        """
        返回推理过程
        :return returnInfo: 推理过程与推理的事实结果
        """
        returnInfo = self.txtStr.copy()
        returnInfo.append("***************************")
        returnInfo.append("********Fact Result********")
        returnInfo.append("***************************")
        for k, v in self.Fact.items():
            returnInfo.append(str(k)+" = "+str(v))
        return returnInfo

    def StoreInfo(self, fileName):
        """
        存储推理过程到文件
        :param fileName: 存储文件名
        """
        storeInfo = self.txtStr
        storeInfo.append("***************************")
        storeInfo.append("********Fact Result********")
        storeInfo.append("***************************")
        for k, v in self.Fact.items():
            storeInfo.append(str(k)+" = "+str(v))
        f = open(fileName, 'w')
        for line in storeInfo:
            line += '\n'
            f.write(line)
        f.close()

# if __name__ == '__main__':
