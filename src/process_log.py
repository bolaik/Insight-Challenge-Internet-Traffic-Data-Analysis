import re
from datetime import datetime
from collections import defaultdict
from datetime import timedelta

# transform time string into time variables
def set_time(date_str):
    # convert datetime string to real time
    time_struct = datetime.strptime(date_str, "%d/%b/%Y:%H:%M:%S %z")
    return(time_struct)

# robust way for split each record
def dict_record(record):
    record_split = re.split("\[|\]", record)
    record_head_split = record_split[0].split()
    record_tail_split = record_split[-1].split()
    if record_tail_split[-1] == "-": record_tail_split[-1] = 0
    # define dictionary of one record
    dic = {"raw":record,
           "host":record_head_split[0], 
           "time":record_split[-2],
           "request":record_tail_split[1:-3],
           "code":record_tail_split[-2],
           "bytes":record_tail_split[-1]}
    return(dic)

# create list of dictionaries of input logins
file_path = "./log_input/log.txt"
record_list = []
with open(file_path, "r+", encoding='utf-8', errors="replace") as text_file:
    for record in text_file:
#        record = text_file.readline()[:-1]
        record_split = dict_record(record)
        record_list.append(record_split)

# rank of host
rank_host = defaultdict(int)
for record in record_list:
    rank_host[record["host"]] += 1
f = open("./log_output/hosts.txt","w+")
for key in sorted(rank_host, key = rank_host.get, reverse=True)[:10]:
    f.write(str(key)+","+str(rank_host[key])+"\n")
f.close()


# rank hot resources
from collections import defaultdict
rank_resource = defaultdict(int)
for record in record_list:
    for resource in record["request"]:
        rank_resource[resource] += int(record["bytes"])
f = open("./log_output/resources.txt", "w+")
for key in sorted(rank_resource, key = rank_resource.get, reverse=True)[:10]:
    f.write(str(key)+"\n")
f.close()


# busiest 60-minute periods
rank_period = {}

t_new = record_list[0]["time"]
t_ini = set_time(t_new)
t_fin = t_ini + timedelta(hours = 1)
for nF in range(1,len(record_list)):
    t_try = set_time(record_list[nF]["time"])
    if t_try > t_fin :
        break
if nF == len(record_list)-1:
    rank_period[t_new] = nF + 1
else:
    rank_period[t_new] = nF
t_old = t_new
    
for nI in range(1, len(record_list)):
    t_new = record_list[nI]["time"]
    if t_new != t_old:
        t_ini = set_time(t_new)
        t_fin = t_ini + timedelta(hours = 1)
        for nF in range(nI+1, len(record_list)):
            t_try = set_time(record_list[nF]["time"])
            if t_try > t_fin:
                break
        if nF == len(record_list)-1:
            rank_period[t_new] = nF - nI + 1
        else:
            rank_period[t_new] = nF - nI
    t_old = t_new
f = open("./log_output/hours.txt", "w+")
for key in sorted(rank_period, key = rank_period.get, reverse=True)[:10]:
    f.write(str(key)+","+str(rank_period[key])+"\n")
f.close()


# detect patterns of three consecutive failed login attempts within 20 seconds
# block further attempts from the IP address for the next 5 minutes
block_list = []
h = open("./log_output/blocked_host.txt", "w+")
while len(record_list) > 0:
    list_to_del = [0]

    if int(record_list[0]["code"]) == 401:
        host = record_list[0]["host"]
        count = 1
        t_ini = set_time(record_list[0]["time"])
        t_fin = t_ini + timedelta(seconds = 20)

        for nF in range(1, len(record_list)):
            t_try = set_time(record_list[nF]["time"])
            host_new = record_list[nF]["host"]
            code_new = record_list[nF]["code"]

            if t_try > t_fin and count < 3: break
            if host_new == host:
                list_to_del.append(nF)
                if count < 3:
                    if int(code_new) == 401: 
                        count += 1
                        if count == 3:
                            blk_fin = t_try + timedelta(minutes = 5)
                            h.write(str(host)+","+str(record_list[nF]["time"])+"\n")
                    else: break
                else:
                    count += 1
                    block_list.append(record_list[nF]["raw"])
                    if t_try > blk_fin: break

    # remove processed items from the record_list
    list_to_del.reverse()
    for item in list_to_del:
        del record_list[item]

h.close()
f = open("./log_output/blocked.txt", "w+")
f.writelines(["%s" % item  for item in block_list[:10]])
f.close()
