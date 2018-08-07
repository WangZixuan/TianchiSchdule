# -*- coding: UTF-8 -*-
'''
    这份代码仅在评测时负责组合数据有效
'''
out = open("problem2.csv",'w')
cnt=0
app_resources_file="./Tianchi/b_app_resources.csv"
machine_resources_file="./Tianchi/b_machine_resources.csv"
app_interference_file="./Tianchi/b_app_interference.csv"
inst_deploy_file="./Tianchi/b_instance_deploy.csv"

for line in open(app_resources_file): cnt+=1
out.write(str(cnt)+'\n')
with open(app_resources_file) as f:
    for line in f:
        out.write(line)

cnt=0
for line in open(machine_resources_file): cnt+=1
out.write(str(cnt)+'\n')

with open(machine_resources_file) as f:
    for line in f:
        out.write(line)

cnt=0
for line in open(inst_deploy_file): cnt+=1
out.write(str(cnt)+'\n')

with open(inst_deploy_file) as f:
    for line in f:
        out.write(line)

cnt=0
for line in open(app_interference_file): cnt+=1
out.write(str(cnt)+'\n')

with open(app_interference_file) as f:
    for line in f:
        out.write(line)

out.close()
# with open('b_app_resources.csv') as f:
    # for line in f:
        # out.write(line)