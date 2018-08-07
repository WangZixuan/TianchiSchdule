# -*- coding: UTF-8 -*-
from util import *
import numpy as np
from functools import reduce

def readAppResources():
    ## app resource
    app_resfile = open(app_resources_file)
    for line in app_resfile:
        line = line.strip('\n')
        vec_resource = line.split(',')
        appid = vec_resource[0]
        cpu = np.array(vec_resource[1].split('|'))
        cpu = cpu.astype(np.float)
        mem = np.array(vec_resource[2].split('|'))
        mem = mem.astype(np.float)
        disk = float(vec_resource[3])
        P = int(vec_resource[4])
        M = int(vec_resource[5])
        PM = int(vec_resource[6])
        app = App(appid,cpu,mem,disk,P,M,PM)
        Apps[appid] = app
        
def readMachineResources():
    ## machine resource
    machine_resfile = open(machine_resources_file)
    for line in machine_resfile:
        line = line.strip('\n')
        vec_resource = line.split(',')
        machineid = vec_resource[0]
        cpu = np.array(vec_resource[1].split('|'))
        cpu = cpu.astype(np.float)
        mem = np.array(vec_resource[2].split('|'))
        mem = mem.astype(np.float)
        disk = int(vec_resource[3])
        P = int(vec_resource[4])
        M = int(vec_resource[5])
        PM = int(vec_resource[6])
        machine = Machine(machineid,cpu,mem,disk,P,M,PM)
        Machines[machineid] = machine

def readInferrence():
    ## machine resource
    inferrence_file = open(app_interference_file)
    for line in inferrence_file:
        line = line.strip('\n')
        vec_resource = line.split(',')
        appa = vec_resource[0]
        appb = vec_resource[1]
        k = int(vec_resource[2])
        Inferrences[appa+" "+appb] = k
        # Inferrences[appb+" "+appa] = k

def readDeploy():
    #读取Inst部署的情况
    #全局变量表示已提前部署的inst
    PreDeploy
    #全局变量表示未提前部署的inst
    NonDeploy
    deploy_file = open(inst_deploy_file)
    for line in deploy_file:
        line = line.strip('\n')
        vec_resource = line.split(',')
        inst = vec_resource[0]
        app = vec_resource[1]
        machine = vec_resource[2]

        if( len(machine) > 1 ):
            PreDeploy.append([inst,app,machine])
        else:
            NonDeploy.append([inst,app,''])
        Insts[inst] = [app,None]
        Apps[app].instance.append(inst)
            
def checkConstraint():
    for machine in Deployments:
        # print(machine)
        localInsts = Deployments[machine]
        AppCounter = {}
        if not len(localInsts):
            continue
        #check cpu
        localCpu = np.zeros((98,), dtype=np.float)
        #check memory
        localMem = np.zeros((98,), dtype=np.float)
        #check disk
        localDisk = 0
        #check P
        localP = 0
        #check M
        localM = 0
        #check PM
        localPM = 0
        for inst in localInsts:
            localCpu +=  Apps[Insts[inst][0]].cpu
            localMem +=  Apps[Insts[inst][0]].mem
            localDisk +=  Apps[Insts[inst][0]].disk
            localP +=  Apps[Insts[inst][0]].P
            localM +=  Apps[Insts[inst][0]].M
            localPM +=  Apps[Insts[inst][0]].PM
        
        # check  cpu
        compare = np.greater_equal(Machines[machine].cpu,localCpu)
        # print(compare)
        compare = reduce(lambda x,y:x&y, compare)
        if(not compare):
            logger.debug("CPU fail on "+machine)
            return False
            # check  mem

        compare = np.greater_equal(Machines[machine].mem,localMem)
        compare = reduce(lambda x,y:x&y, compare)
        if(not compare):
            logger.debug("Memory fail on "+machine)
            return False

        # check  disk
        compare = Machines[machine].disk >= localDisk
        if(not compare):
            logger.debug("disk fail on "+machine)
            return False

        # check  P
        compare = Machines[machine].P >= localP
        if(not compare):
            logger.debug("P fail on "+machine)
            return False
        
        # check  M
        compare = Machines[machine].M >= localM
        if(not compare):
            ("M fail on "+machine)
            return False

        # check  PM
        compare = Machines[machine].PM >= localPM
        if(not compare):
            logger.debug("PM fail on "+machine)
            return False    

        #check inferrence
        for inst in localInsts:
            curApp = Insts[inst][0]
            if curApp not in AppCounter:
                AppCounter[curApp] = 1
            else:
                AppCounter[curApp] += 1
        
        for appa in curApp:
            for appb in curApp:
                if appa+" "+appb in Inferrences:
                        if AppCounter[appb] > Inferrences[appa+" "+appb]:
                            print ("Inferrence between "+appa+" "+appb+" broken "+"on "+machine)
                            return False
        #constraint satisfy 
    return True
