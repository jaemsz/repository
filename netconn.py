# Tool to lookup IP addresses in the TCP table
# It can also:
# 1.  Add IP address entries into a mongo DB
# 2.  Diff scanned IP addresses with existing addresses in the DB
# 3.  Provide JSON output of the IP addresses including:
#     a.  filename
#     b.  command line
#     c.  file SHA256
#     d.  source address
#     e.  destination address

from ctypes import *
import socket
import struct
import psutil
import json
import hashlib
import os
import sys
import pymongo

FILENAME_EXCLUSIONS = [
    "firefox.exe"
]

IP_EXCLUSIONS = [
    "0.0.0.0",
    "127.0.0.1",
    "172.16.0.154",
]

OUTPUT_NORMAL = 0
OUTPUT_JSON = 1
OUTPUT_TABLE = 2
OUTPUT_DIFF = 3
OUTPUT_DUMP = 4
OUTPUT_DROP = 5

NO_ERROR = 0
ERROR_INSUFFICIENT_BUFFER = 122

MIB_TCP_STATE_CLOSED = 1
MIB_TCP_STATE_LISTEN = 2
MIB_TCP_STATE_SYN_SENT = 3
MIB_TCP_STATE_SYN_RCVD = 4
MIB_TCP_STATE_ESTAB = 5
MIB_TCP_STATE_FIN_WAIT1 = 6
MIB_TCP_STATE_FIN_WAIT2 = 7
MIB_TCP_STATE_CLOSE_WAIT = 8
MIB_TCP_STATE_CLOSING = 9
MIB_TCP_STATE_LAST_ACK = 10
MIB_TCP_STATE_TIME_WAIT = 11
MIB_TCP_STATE_DELETE_TCB = 12

TcpConnectionOffloadStateInHost = 0
TcpConnectionOffloadStateOffloading = 1
TcpConnectionOffloadStateOffloaded = 2
TcpConnectionOffloadStateUploading = 3
TcpConnectionOffloadStateMax = 4

class MIB_TCPROW2(Structure):
    _fields_ = [
        ("dwState", c_ulong),
        ("dwLocalAddr", c_ulong),
        ("dwLocalPort", c_ulong),
        ("dwRemoteAddr", c_ulong),
        ("dwRemotePort", c_ulong),
        ("dwOwningPid", c_ulong),
        ("dwOffloadState", c_ulong),
    ]
    
def MIB_TCPTABLE2_FACTORY(size):
    class MIB_TCPTABLE2(Structure):
        _fields_ = [
            ("dwNumEntries", c_ulong),
            ("table", MIB_TCPROW2 * size),
        ]
    return MIB_TCPTABLE2()
    
def state_to_string(state):
    if state == MIB_TCP_STATE_CLOSED:
        return "MIB_TCP_STATE_CLOSED"
    elif state == MIB_TCP_STATE_LISTEN:
        return "MIB_TCP_STATE_LISTEN"
    elif state == MIB_TCP_STATE_SYN_SENT:
        return "MIB_TCP_STATE_SYN_SENT"
    elif state == MIB_TCP_STATE_SYN_RCVD:
        return "MIB_TCP_STATE_SYN_RCVD"
    elif state == MIB_TCP_STATE_ESTAB:
        return "MIB_TCP_STATE_ESTAB"
    elif state == MIB_TCP_STATE_FIN_WAIT1:
        return "MIB_TCP_STATE_FIN_WAIT1"
    elif state == MIB_TCP_STATE_FIN_WAIT2:
        return "MIB_TCP_STATE_FIN_WAIT2"
    elif state == MIB_TCP_STATE_CLOSE_WAIT:
        return "MIB_TCP_STATE_CLOSE_WAIT"
    elif state == MIB_TCP_STATE_CLOSING:
        return "MIB_TCP_STATE_CLOSING"
    elif state == MIB_TCP_STATE_LAST_ACK:
        return "MIB_TCP_STATE_LAST_ACK"
    elif state == MIB_TCP_STATE_TIME_WAIT:
        return "MIB_TCP_STATE_TIME_WAIT"
    elif state == MIB_TCP_STATE_DELETE_TCB:
        return "MIB_TCP_STATE_DELETE_TCB"
    else:
        return "<UNKNOWN>"
        
def get_sha256_from_path(file_path):
    with open(file_path, "rb") as f:
        contents = f.read()
        sha256 = hashlib.sha256(contents).hexdigest()
    return sha256

def get_sha256_from_cmd_line(command_line):
    if not command_line:
        return "<UNKNOWN>"
    else:
        file_path = command_line[0]
        dir_path = os.path.dirname(file_path)
        if not dir_path:
            return "<UNKNOWN>"
        else:
            return get_sha256_from_path(file_path)   
    
def isPE(file_path):
    with open(file_path, "rb") as f:
        contents = f.read(2)
    if contents[0] == 0x4D and contents[1] == 0x5A:
        # TODO: Need to check more fields
        return True
    return False

def get_loaded_modules_list(pid):
    loaded_modules = []
    try:
        p = psutil.Process(pid)
        for dll in p.memory_maps():
            if isPE(dll.path):
                loaded_modules.append({
                    "module_path" : dll.path,
                    "module_sha256" : get_sha256_from_path(dll.path),
                })
    except:
        return []
    return loaded_modules
    
def get_data():
    pid_ip_map = {}
    
    windll.iphlpapi.GetTcpTable2.argtypes = [c_void_p, POINTER(c_ulong), c_bool]
    tcp_table_size = c_ulong()
    
    ret = windll.iphlpapi.GetTcpTable2(None, byref(tcp_table_size), True)
    if ret == ERROR_INSUFFICIENT_BUFFER:
        tcp_table = MIB_TCPTABLE2_FACTORY(tcp_table_size.value)
        
        ret = windll.iphlpapi.GetTcpTable2(byref(tcp_table), byref(tcp_table_size), True)
        if ret != NO_ERROR:
            print("ERROR: GetTcpTable2() failed, error = " + str(ret))
        else:
            for i in range(tcp_table.dwNumEntries):
                src_ip = socket.inet_ntoa(struct.pack('<L', tcp_table.table[i].dwLocalAddr))
                dst_ip = socket.inet_ntoa(struct.pack('<L', tcp_table.table[i].dwRemoteAddr))
                src_port = tcp_table.table[i].dwLocalPort
                dst_port = tcp_table.table[i].dwRemotePort
                pid = tcp_table.table[i].dwOwningPid
                state = state_to_string(tcp_table.table[i].dwState)
                cmd_line = psutil.Process(pid).cmdline()
                
                if pid not in pid_ip_map:
                    pid_ip_map[pid] = {
                        "filename" : psutil.Process(pid).name(),
                        "cmd_line" : cmd_line,
                        "sha256" : get_sha256_from_cmd_line(cmd_line),
                        "loaded_modules" : get_loaded_modules_list(pid),
                        "connections" : [
                            {
                                "src" : src_ip + ":" + str(src_port),
                                "dst" : dst_ip + ":" + str(dst_port), 
                                "state" : state,
                            }
                        ]
                    }
                else:
                    pid_ip_map[pid]["connections"].append(
                        {
                            "src" : src_ip + ":" + str(src_port),
                            "dst" : dst_ip + ":" + str(dst_port),
                            "state" : state,
                        }
                    )
    return pid_ip_map
    
def is_dst_in_table(col, dst):
    found = False
    try:
        items = col.find({"dst" : dst})
        if items[0]:
            found = True
    except IndexError:
        pass
    return found
    
def save_to_table(pid_ip_map):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["security"]
    col = db["gettcptable2"]
    
    for pid in pid_ip_map:
        filename = pid_ip_map[pid]["filename"]
        if filename not in FILENAME_EXCLUSIONS:
            for conn in pid_ip_map[pid]["connections"]:
                dst = conn["dst"]
                found = is_dst_in_table(col, dst)
                if not found and dst.split(":")[0] not in IP_EXCLUSIONS:
                    x = col.insert_one({"dst" : dst})
                    print("DB: {}".format(dst))
    
def output_diff_dst(pid_ip_map):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["security"]
    col = db["gettcptable2"]
    
    for pid in pid_ip_map:
        filename = pid_ip_map[pid]["filename"]
        if filename not in FILENAME_EXCLUSIONS:
            for conn in pid_ip_map[pid]["connections"]:
                dst = conn["dst"]
                found = is_dst_in_table(col, dst)
                if not found and dst.split(":")[0] not in IP_EXCLUSIONS:
                    print("DIFF: {}".format(dst))
    
def dump_table():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["security"]
    col = db["gettcptable2"]
    
    for row in col.find():
        print(row)
    
def drop_table():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["security"]
    col = db["gettcptable2"]
    col.drop()
        
def main(output_type):
    if output_type == OUTPUT_DUMP:
        dump_table()
        return
    
    if output_type == OUTPUT_DROP:
        drop_table()
        return
    
    pid_ip_map = get_data()
    
    # print out the TCP connections
    if output_type == OUTPUT_NORMAL:
        for pid in pid_ip_map:
            print("PID: " + str(pid))
            print("Process Name: " + psutil.Process(pid).name())
            print("SHA256: " + pid_ip_map[pid]["sha256"])
            for c in pid_ip_map[pid]["connections"]:
                print("{:10}{:25}{:10}{:25}{:10}{:25}".format("SRC: ", c.get("src"), "DST: ", c.get("dst"), "STATE: ", c.get("state")))
            print()
        return
        
    if output_type == OUTPUT_JSON:
        print(json.dumps(pid_ip_map, indent=4))
        return
        
    if output_type == OUTPUT_TABLE:
        save_to_table(pid_ip_map)
        return
        
    if output_type == OUTPUT_DIFF:
        output_diff_dst(pid_ip_map)
        return
    
if __name__ == "__main__":
    output_type = OUTPUT_NORMAL
    if len(sys.argv) == 2:
        if sys.argv[1] == "JSON":
            output_type = OUTPUT_JSON
        elif sys.argv[1] == "DB":
            output_type = OUTPUT_TABLE
        elif sys.argv[1] == "DIFF":
            output_type = OUTPUT_DIFF
        elif sys.argv[1] == "DUMP":
            output_type = OUTPUT_DUMP
        elif sys.argv[1] == "DROP":
            output_type = OUTPUT_DROP
    main(output_type)
