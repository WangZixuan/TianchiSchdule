# -*- coding: UTF-8 -*-
import numpy as np
from functools import reduce
import logging
import logging.handlers

#设置log文件用于debug
LOG_FILE = './output/log.log' 
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler 
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
 
formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter
 
logger = logging.getLogger('log')    # 获取名为tst的logger
logger.addHandler(handler)           # 为logger添加handler
logger.setLevel(logging.DEBUG)

# 全局变量，APP存放APP的对象,key为app的id, value为APP对象实例
Apps = {}  

#全局变量 存放每个机器类 key为机器的id, value为机器对象实例
Machines = {}

#全局变量 存放每个App之间的Inferrence key为appa+' '+appb， value为 约束值
Inferrences = {}

#全局变量 存放每个Insts实例类
Insts = {}

#全局变量 存放当前的部部署情况, key为inst的id, value为二元组[appid,machine_id],app_id代表对应的app的编号,machine_id为空代表没有部署
Deployments = {}

#全局变量表示已提前部署的inst
PreDeploy = []

#全局变量表示未提前部署的inst
NonDeploy = []

#app的资源约束文件
app_resources_file="./Tianchi/b_app_resources.csv"

#机器资源描述文件
machine_resources_file="./Tianchi/b_machine_resources.csv"

#app之间干预情况文件
app_interference_file="./Tianchi/b_app_interference.csv"

#inst的布置情况文件
inst_deploy_file="./Tianchi/b_instance_deploy.csv"
#solution 输出文件
solution_file = "./output/solution2.csv"

class App:
    def __init__(self,appid,cpu_res,mem_res,disk,P,M,PM):
        self.id = appid  # App的id
        self.cpu = cpu_res # App的cpu资源向量
        self.mem = mem_res # App的memory资源向量
        self.disk = disk  # APP的disk标量
        self.P = P  # APP的P标量
        self.M = M  # APP的M标量
        self.PM = PM # PM 标量
        self.instance = [] # 属于该app的实例的id

class Machine:
    '''
        机器类
            - 成员变量
                1. 放置到该机器上的Inst的List： insts(set)
                2. 机器上每一个部署的app的数目： appCounter(dictionary)
                3. 机器的id： id(string)
                4. cpu的资源总量: cpu(1*98 numpy array)
                5. memory的资源总量: mem(1*98 numpy array)
                6. disk的资源总量: disk(标量)
                7. P: P(标量)
                8. M: M(标量)
                9. PM: PM(标量)
                10. cpu的使用率: cpurate(float)
                11. cpu使用率上限(optional): cputhreshold(float)
                12. 剩余cpu资源: rcpu(1*98 numpy array)
                13. 剩余mem资源: rmem(1*98 numpy array)
                14. 剩余disk资源: rdisk(标量)
                15. 剩余P资源: rP()
                16. 剩余M资源: 
            - 成员函数
                1.init 初始化
                2.available(self,inst_id): 检测inst_id(string) 能否插入当前机器
                3.available(self,inst_id): 检测inst_id(string) 能否插入当前机器
                4.availableThreshold(self,inst_id): 检测限定threshold情况下是否添加inst到machine中去
                5.add_inst(self,inst_id):添加实例inst_id进入当前的机器
                6.remove(self,inst_id):移出实例inst_id
            
    '''
    def __init__(self,machine_id,cpu_res,mem_res,disk,P,M,PM):
        self.insts = set([])
        self.appCounter={}
        self.id = machine_id
        self.cpu = cpu_res
        self.mem = mem_res
        self.disk = disk
        self.P = P
        self.M = M
        self.PM = PM
        #cpu 使用rate 上限默认 0.5
        self.cpurate = 0.0
        self.cputhreshold = 0.5
        # 剩余资源情况
        self.rcpu = cpu_res
        self.rmem = mem_res
        self.rdisk = disk
        self.rP = P
        self.rM = M
        self.rPM = PM

    def available(self,inst_id):
        curApp = Apps[Insts[inst_id][0]]
        
        # check  cpu
        compare = np.greater_equal(self.cpu, self.cpu-self.rcpu+curApp.cpu)
        compare = reduce(lambda x,y:x&y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate cpu on "+ self.id)
            return False
    
        # check  mem
        compare = np.greater_equal(self.rmem,curApp.mem)
        compare = reduce(lambda x,y:x&y, compare)
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate mem on "+ self.id)
            return False

        # check  disk
        compare = self.rdisk >= curApp.disk
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate disk on "+ self.id)
            return False

        # check  P
        compare = self.rP >= curApp.P
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate P on "+ self.id)
            return False
        
        # check  M
        compare = self.rM >= curApp.M
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate M on "+ self.id)
            return False

        # check  PM
        compare = self.rPM >= curApp.PM
        if(not compare):
            # logger.debug(inst_id+" fails to acllocate PM on "+ self.id)
            return False    

        #check inferrence
        try:
            for appa in self.appCounter:
                if appa+" "+curApp.id in Inferrences:
                    if curApp.id not in self.appCounter:
                        if 1 > Inferrences[appa+" "+curApp.id]:
                            logger.debug(inst_id+" Inferrence0 between "+appa+" "+curApp.id+" broken "+"on "+ self.id)
                            # logger.debug(inst_id,str(self.insts),self.id)
                            # print(Inferrences[appa+" "+curApp.id])
                            return False
                    elif self.appCounter[curApp.id]+1 > (Inferrences[appa+" "+curApp.id]+(appa==curApp.id)):
                        logger.debug (inst_id+"Inferrence2 between "+appa+" "+curApp.id+" broken "+"on "+ self.id)
                        # logger.debug(inst_id,str(self.insts),self.id)
                        return False

                if curApp.id+" "+appa in Inferrences:
                    # if curApp.id not in self.appCounter:
                    if (self.appCounter[appa] + (appa==curApp.id)) > (Inferrences[curApp.id+" "+appa] + (appa==curApp.id)):
                        logger.debug(inst_id+" Inferrence3 between "+curApp.id+" "+appa+" broken "+"on "+ self.id)
                        return False
        except:
            logger.debug("Bad error allocate "+ inst_id +" of App "+curApp.id)
        #constraint satisfy 
        return True

    def availableThreshold(self,inst_id):
        curApp = Apps[Insts[inst_id][0]]
        # check  cpu
        compare = np.greater_equal(self.cpu*self.cputhreshold, self.cpu*self.cputhreshold-self.rcpu+curApp.cpu)
        compare = reduce(lambda x,y:x&y, compare)
        if(not compare):
            logger.debug(inst_id+" fails to acllocate cpu on "+ self.id)
            return False
    
        # check  memory
        compare = np.greater_equal(self.rmem,curApp.mem)
        compare = reduce(lambda x,y:x&y, compare)
        if(not compare):
            logger.debug(inst_id+" fails to acllocate mem on "+ self.id)
            return False

        # check  disk
        compare = self.rdisk >= curApp.disk
        if(not compare):
            logger.debug(inst_id+" fails to acllocate disk on "+ self.id)
            return False
        
        # check  P
        compare = self.rP >= curApp.P
        if(not compare):
            logger.debug(inst_id+" fails to acllocate P on "+ self.id)
            return False
        
        # check  M
        compare = self.rM >= curApp.M
        if(not compare):
            logger.debug(inst_id+" fails to acllocate M on "+ self.id)
            return False

        # check  PM
        compare = self.rPM >= curApp.PM
        if(not compare):
            logger.debug(inst_id+" fails to acllocate PM on "+ self.id)
            return False    

        #check inferrence
        try:
            for appa in self.appCounter:
                if appa+" "+curApp.id in Inferrences:
                    if curApp.id not in self.appCounter:
                        if 1 > Inferrences[appa+" "+curApp.id]:
                            logger.debug(inst_id+" Inferrence0 between "+appa+" "+curApp.id+" broken "+"on "+ self.id)
                            # logger.debug(inst_id,str(self.insts),self.id)
                            # print(Inferrences[appa+" "+curApp.id])
                            return False
                    elif self.appCounter[curApp.id]+1 > (Inferrences[appa+" "+curApp.id]+(appa==curApp.id)):
                        logger.debug (inst_id+"Inferrence2 between "+appa+" "+curApp.id+" broken "+"on "+ self.id)
                        # logger.debug(inst_id,str(self.insts),self.id)
                        return False

                if curApp.id+" "+appa in Inferrences:
                    # if curApp.id not in self.appCounter:
                    if (self.appCounter[appa] + (appa==curApp.id)) > (Inferrences[curApp.id+" "+appa] + (appa==curApp.id)):
                        logger.debug(inst_id+" Inferrence3 between "+curApp.id+" "+appa+" broken "+"on "+ self.id)
                        return False
        except:
            logger.debug("Bad error allocate "+ inst_id +" of App "+curApp.id)
        
        #constraint satisfy 
        return True

    def add_inst(self,inst_id):
        # 检查是否可以插入
        # if not self.available(inst_id):
            # return False        
        # 添加实例inst到machine 的 list中
        self.insts.add(inst_id)
        
        #添加当前的app到machine的计数中
        if Insts[inst_id][0] not in self.appCounter:
            self.appCounter[Insts[inst_id][0]] = 1
        else:
            self.appCounter[Insts[inst_id][0]] += 1
        
        # 计算剩余cpu资源
        self.rcpu = self.rcpu - Apps[Insts[inst_id][0]].cpu
        #计算cpu的使用率
        self.cpurate = max((self.cpu-self.rcpu)/self.cpu)
        
        # 计算剩余mem资源
        self.rmem = self.rmem - Apps[Insts[inst_id][0]].mem
        
        # 计算剩余disk资源
        self.rdisk = self.rdisk - Apps[Insts[inst_id][0]].disk
        
        # 计算剩余P资源
        self.rP = self.rP - Apps[Insts[inst_id][0]].P
        
        # 计算剩余M资源
        self.rM = self.rM - Apps[Insts[inst_id][0]].M
        
        # 计算剩余PM资源
        self.rPM = self.rPM - Apps[Insts[inst_id][0]].PM
        
        #返回已添加
        return True

    def remove(self,inst_id):
        # 从machine 的 list中 移出inst
        self.insts.remove(inst_id)
        
        #添加当前的app到machine的计数中
        self.appCounter[Insts[inst_id][0]] -= 1
        if self.appCounter[Insts[inst_id][0]]==0 :
            del self.appCounter[Insts[inst_id][0]]
        
        # 计算剩余cpu资源
        self.rcpu = self.rcpu + Apps[Insts[inst_id][0]].cpu
        #计算cpu的使用率
        self.cpurate = max((self.cpu-self.rcpu)/self.cpu)
        
        # 计算剩余mem资源
        self.rmem = self.rmem + Apps[Insts[inst_id][0]].mem
        
        # 计算剩余disk资源
        self.rdisk = self.rdisk + Apps[Insts[inst_id][0]].disk
        
        # 计算剩余P资源
        self.rP = self.rP + Apps[Insts[inst_id][0]].P
        
        # 计算剩余M资源
        self.rM = self.rM + Apps[Insts[inst_id][0]].M
        
        # 计算剩余PM资源
        self.rPM = self.rPM + Apps[Insts[inst_id][0]].PM
        
        #返回已添加
        return True
        
