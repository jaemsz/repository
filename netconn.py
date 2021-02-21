from ctypes import *
import socket
import struct
import psutil

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
        
def main():
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
                dest_ip = socket.inet_ntoa(struct.pack('<L', tcp_table.table[i].dwRemoteAddr))
                pid = tcp_table.table[i].dwOwningPid
                if pid not in pid_ip_map:
                    state = state_to_string(tcp_table.table[i].dwState)
                    pid_ip_map[pid] = [{
                        "dest_ip" : dest_ip, 
                        "state" : state,
                    }]
                else:
                    if dest_ip not in pid_ip_map[pid]:
                        pid_ip_map[pid].append({
                            "dest_ip" : dest_ip,
                            "state" : state,
                        })
    
    # print out the TCP connections
    for pid in pid_ip_map:
        print("PID: " + str(pid))
        print("Process Name: " + psutil.Process(pid).name())
        for ip in pid_ip_map[pid]:
            print("\t" + ip.get("dest_ip") + "\t" + ip.get("state"))
    
if __name__ == "__main__":
    main()
