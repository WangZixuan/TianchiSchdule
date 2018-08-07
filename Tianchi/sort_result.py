# -*- coding: UTF-8 -*-
# 测试程序，无需运行
Pre_order = {}
Machine_order = []
cMachineDeploy = {}
cInstDeploy = {}
MachineDeploy = {}
InstDeploy = {}
out  = open('fesiable.csv','w')
# order  = open('order.csv','w')

def readCnt():
    with open('Sort_deployment.csv') as deploy_file:
        cnt = 0
        for line in deploy_file:
            line = line.strip('\n')
            vec_resource = line.split(',')
            inst = vec_resource[0]
            machine = vec_resource[2]
            if( len(machine) > 1 ):
                if(machine not in cMachineDeploy):
                    cMachineDeploy[machine]=[inst]
                else:    
                    cMachineDeploy[machine].append(inst)
                cnt+=1
            else:
                return cnt

def orderDeploy(cnt):
    ## deployment
    deploy_file = open('result2.csv')
    curcnt = 0
    for line in deploy_file:   
        curcnt += 1
        if( curcnt > cnt ):
            if len(Machine_order) > 0:
                t = list(Machine_order)
                t.reverse()
                for x in t:
                    if x in cMachineDeploy:
                        for i in cMachineDeploy[x]:
                            # print(x,InstDeploy[i],x==InstDeploy[i])
                            if x != InstDeploy[i]:
                                out.write(i+','+InstDeploy[i]+'\n')
                                del InstDeploy[i]
                for item in InstDeploy:
                    out.write(item+","+InstDeploy[item]+'\n')
                Machine_order[:]=[]
            out.write(line)
        else:
            line1 = line.strip('\n')
            vec_resource = line1.split(',')
            inst = vec_resource[0]
            machine = vec_resource[1]
            InstDeploy[inst]=machine
            if machine not in MachineDeploy:
                MachineDeploy[machine]=[inst]
            else:
                MachineDeploy[machine].append(inst)
            # if cMachineDeploy
            if(machine not in Machine_order):
                Machine_order.append(machine)

if __name__ == '__main__':
    # Machine_order = set(reversed(Machine_order))
    cnt = readCnt()
    print(cnt)
    orderDeploy(cnt)
    # print len(Machines)
    # print(len(Apps))