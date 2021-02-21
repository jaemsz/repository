from ctypes import *
import socket
import struct
import psutil
import json
import hashlib
import os
import sys

OUTPUT_NORMAL = 0
OUTPUT_JSON = 1

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
        
def get_sha256(command_line):
    if not command_line:
        return "<UNKNOWN>"
    else:
        file_path = command_line[0]
        dir_path = os.path.dirname(file_path)
        if not dir_path:
            return "<UNKNOWN>"
        else:
            with open(file_path, "rb") as f:
                contents = f.read()
                sha256 = hashlib.sha256(contents).hexdigest()
            return sha256
    
def main(output_type):
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
                sha256 = get_sha256(cmd_line)
                
                if pid not in pid_ip_map:
                    pid_ip_map[pid] = {
                        "filename" : psutil.Process(pid).name(),
                        "cmd_line" : cmd_line,
                        "sha256" : sha256,                        
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
    
    # print out the TCP connections
    if output_type == OUTPUT_NORMAL:
        for pid in pid_ip_map:
            print("PID: " + str(pid))
            print("Process Name: " + psutil.Process(pid).name())
            print("SHA256: " + pid_ip_map[pid]["sha256"])
            for c in pid_ip_map[pid]["connections"]:
                print("{:10}{:25}{:10}{:25}{:10}{:25}".format("SRC: ", c.get("src"), "DST: ", c.get("dst"), "STATE: ", c.get("state")))
            print()
    else:
        print(json.dumps(pid_ip_map, indent=4))
    
if __name__ == "__main__":
    output_type = OUTPUT_NORMAL
    if len(sys.argv) == 2 and sys.argv[1] == "JSON":
        output_type = OUTPUT_JSON
    main(output_type)
