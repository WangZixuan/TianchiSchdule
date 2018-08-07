# -*- coding: UTF-8 -*-
from util import *
from readFile import *
import sys

global usedMachine 
global unusedMachine

outfile = open(solution_file,'w')

def reallocate(inst_id, machine_id=""):
    find = False
    #优先使用已经占用的机器
    for machine in usedMachine:
        if len(machine_id) > 1:
            if find:
                if Machines[machine].available(inst_id):
                    Machines[machine].add_inst(inst_id)
                    return machine
            elif machine == machine_id:
                find = True
        else:
            if Machines[machine].available(inst_id):
                Machines[machine].add_inst(inst_id)
                return machine
            
    # 使用空闲机器
    for machine in unusedMachine:
        if Machines[machine].available(inst_id):
            Machines[machine].add_inst(inst_id)
            unusedMachine.remove(machine)
            usedMachine.append(machine)
            return machine
    assert(0)

def assign(inst_id,machine_id=""):
    if(len(machine_id)>1):
        #指定machine 布置  
        if machine_id in unusedMachine:
            unusedMachine.remove(machine_id)
            usedMachine.append(machine_id)
        
        if(Machines[machine_id].available(inst_id)):
            Machines[machine_id].add_inst(inst_id)
            return machine_id
        else:
            machine = reallocate(inst_id,machine_id)
            return machine
    else:
        machine = reallocate(inst_id)
        return machine
        
    assert(0)
    # return machine_id

def deploy():
    '''
        按照顺序部署每一个inst
    '''    
    megerdDeployment = PreDeploy + NonDeploy
    rawOutput = []
    count = len(megerdDeployment)
    index = 0.0
    for item in megerdDeployment:
        index+=1
        if(index%1000):
            print("Progress " + str(index/count*100)+"%")
        [inst,app,machine] = item
        # print("Deploying inst------ "+inst)
        if( len(machine) > 1 ):
            machine = assign(inst,machine)
        else:
            machine = assign(inst)
        try:
            if machine not in Deployments:
                Deployments[machine]=set([])
            Deployments[machine].add(inst)
            Insts[inst][1] = machine
            rawOutput.append([inst,app,machine])
        except:
            assert(0)
            logger.debug(inst+" "+str(machine))
    sortOutput(rawOutput)
    return 0

def sortOutput(rawOutput):
    '''
    对结果排序输出
    '''
    Machine_order = []
    cMachineDeploy = {}
    MachineDeploy = {}
    InstDeploy = {}
    cnt = len(PreDeploy)
    for item in PreDeploy:
        [inst,app,machine] = item
        if( len(machine) > 1 ):
            if(machine not in cMachineDeploy):
                cMachineDeploy[machine]=[inst]
            else:    
                cMachineDeploy[machine].append(inst)
            cnt+=1
        else:
            break
    curcnt = 0
    for item in rawOutput:   
        curcnt += 1
        [inst, app, machine] = item
        if curcnt > cnt :
            if len(Machine_order) > 0:
                t = list(Machine_order)
                t.reverse()
                for x in t:
                    if x in cMachineDeploy:
                        for i in cMachineDeploy[x]:
                            if x != InstDeploy[i]:
                                outfile.write(i+','+InstDeploy[i]+'\n')
                                del InstDeploy[i]
                for item in InstDeploy:
                    outfile.write(inst+","+InstDeploy[inst]+'\n')
                Machine_order[:]=[]
            outfile.write(inst+","+InstDeploy[inst]+'\n')
        else:
            InstDeploy[inst]=machine
            if machine not in MachineDeploy:
                MachineDeploy[machine]=[inst]
            else:
                MachineDeploy[machine].append(inst)
            # if cMachineDeploy
            if(machine not in Machine_order):
                Machine_order.append(machine)
    return 0;
    
if __name__ == '__main__':
    readAppResources()
    readMachineResources()
    readInferrence()
    readDeploy()
    usedMachine = []
    unusedMachine = [x for x in Machines]
    deploy()
    # sortOutput()