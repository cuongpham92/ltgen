import time
import datetime
import os
import sys
import utilize.time_process as time_process, utilize.timetable_process as timetable_process, utilize.file_operations as fifo

TIMES = int(sys.argv[1])

FW_ADDR = "10.0.2.14"

def get_ptc_weight(weight_line):
    ptc_list = weight_line.split(" ")
    http_weight = ptc_list[0]
    imap_weight = ptc_list[1]
    smtp_weight = ptc_list[2]
    ftp_weight = ptc_list[3]

    return http_weight, smtp_weight, imap_weight, ftp_weight

# Read rate input file
lines = fifo.read_file("rate_weight")
rate_list = []
ptc_weight_list = []
pcap_name_list = []

for i, line in enumerate(lines):
    if (i%2 == 0):
        elements = line.split(" ")
        rate_list.append(elements[0])
        pcap_name_list.append(elements[1])
    else:
        ptc_weight_list.append(line)

print(rate_list)
print(ptc_weight_list)

for k in range(0, len(ptc_weight_list)):
    for i in range(0, TIMES):
        time.sleep(120)
        current_time = time_process.get_current_time_minute()
        # Get start time and end time for the interval
        start_itv = time_process.get_next_time_minute(current_time, 2)
        end_itv = time_process.get_next_time_minute(start_itv, 15)

        # Write config file for the main function
        rate = "{0}-{1} {2}".format(start_itv, end_itv, rate_list[k])
        ptc_weight = "{0}".format(ptc_weight_list[k])
        fifo.write_file("rate_timetable.txt", "w", rate)
        fifo.write_file("protocol_weight.txt", "w", ptc_weight)

        # Start suricata
        command = "sshpass -p 'securite' ssh -o StrictHostKeyChecking=no root@10.0.2.20 \"suricata -c /etc/suricata/suricata.yaml -i eth2 -i eth3 -i eth0 -i eth1 &> /root/suricata_logs &\""
        print(command)
        os.system(command)

        command = "ssh -o StrictHostKeyChecking=no client@10.0.2.18 -f \"python3 /home/client/trf-gen-s2/src/http/http_actions.py >> /home/client/attack_logs \""
        print(command)
        os.system(command)

        # Start main function
        os.system("python3 main.py")
        print("python3 main.py")


        # End suricata
        os.system("sshpass -p 'securite' ssh -o StrictHostKeyChecking=no root@10.0.2.20 \"ps aux | grep suricata | grep -v grep | awk '{print \$2}' | xargs sudo kill -9\"")

        # Copy and delete traffic to other machine
        os.system("sshpass -p 'securite' ssh -o StrictHostKeyChecking=no root@10.0.2.20 \"cp /var/log/suricata/fast.log /var/log/suricata/fast.log{0}\"".format(i))
        os.system("sshpass -p 'securite' ssh -o StrictHostKeyChecking=no root@10.0.2.20 \"cp /var/log/suricata/stats.log /var/log/suricata/stats.log{0}\"".format(i))
        os.system("sshpass -p 'securite' ssh -o StrictHostKeyChecking=no root@10.0.2.20 \"> /var/log/suricata/fast.log\"".format(i))
        os.system("sshpass -p 'securite' ssh -o StrictHostKeyChecking=no root@10.0.2.20 \"> /var/log/suricata/stats.log\"".format(i))
