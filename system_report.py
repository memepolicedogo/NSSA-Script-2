#!/bin/python
import os
import socket
import subprocess
import shutil
import psutil
import json
import datetime


def main():
    # ram info
    mem_total = False
    mem_avail = False
    with open("/proc/meminfo") as mfile:
        for line in mfile.readlines():
            if "MemTotal" in line:
                mem_total = line.split(':')[-1].strip(" \t\nkB")
            elif "MemAvailable" in line:
                mem_avail= line.split(':')[-1].strip(" \t\nkB")
            if mem_total and mem_avail:
                break

    # CPU info
    cpu_model = False
    cpu_cores = False
    cpu_proc = False
    with open("/proc/cpuinfo") as cfile:
        for line in cfile.readlines():
            if "model name" in line:
                cpu_model = line.split(':')[-1].strip()
            elif "cpu cores" in line:
                cpu_cores = line.split(':')[-1].strip()
            elif "siblings" in line:
                cpu_proc = line.split(':')[-1].strip()
            if cpu_model and cpu_cores and cpu_proc:
                break

    # Storage info
    str_total, str_used, str_free = shutil.disk_usage("/")

    # OS Info
    hostname = os.uname().nodename
    os_kern = os.uname().release
    os_name = False
    os_ver = False
    with open("/etc/os-release") as ofile:
        for line in ofile.readlines():
            if "PRETTY_NAME" in line:
                os_name = line.split('=')[-1].strip(" \n\t\'\"")
            elif "VERSION_ID" in line:
                os_ver = line.split('=')[-1].strip(" \n\t\'\"")
            if os_name and os_ver:
                break
    # Network info 
    dns1 = False
    dns2 = False
    ip = False
    mask = False
    device = ""
    netinfo = json.loads(subprocess.run(['ip', '-j', 'addr'], capture_output=True).stdout)
    for dev in netinfo:
        if dev["ifname"] == "lo":
            continue
        for addr in dev["addr_info"]:
            if addr["family"] == "inet":
                ip = addr["local"]
                mask = addr["prefixlen"]
                device = dev["ifname"]
                break
        break
    gwinfo = json.loads(subprocess.run(['ip', '-j', 'route'], capture_output=True).stdout)
    gateway = False
    for dev in gwinfo:
        if dev["dev"] == device and dev["dst"] == "default":
            gateway = dev["gateway"]
    with open("/etc/resolv.conf") as nfile:
        for line in nfile.readlines():
            if "nameserver" in line:
                if dns1:
                    dns2 = line.split(' ')[-1].strip()
                    break
                dns1 = line.split(' ')[-1].strip()
    
    output = f"""
                    System Report - {datetime.datetime.now().strftime("%B %d, %Y")}
Device Information
Hostname:                   {hostname}

Network Information
IP Address:                 {ip}/{mask}
Gateway:                    {gateway}
DNS1:                       {dns1}
DNS2:                       {dns2}

Operating System Information
Operating System:           {os_name}
OS Version:                 {os_ver}
Kernel Version:             {os_kern}

Storage Information
System Drive Total:         {int(str_total)/1000000:,.0f} GiB
System Drive Used:          {int(str_used)/1000000:,.0f} GiB
System Drive Free:          {int(str_free)/1000000:,.0f} GiB

Processor Information
CPU Model:                  {cpu_model}
Number of Processors:       {cpu_proc}
Number of Cores:            {cpu_cores}

Memory Information
Total RAM:                  {int(mem_total)/1000000:,.2f} GiB
Avaliable RAM:              {int(mem_avail)/1000000:,.2f} GiB
    """
    print(output)

if __name__ == "__main__":

    main()
