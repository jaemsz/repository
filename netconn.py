from ctypes import *
import socket
import struct

NO_ERROR = 0
ERROR_INSUFFICIENT_BUFFER = 122

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
                    pid_ip_map[pid] = [dest_ip]
                else:
                    if dest_ip not in pid_ip_map[pid]:
                        pid_ip_map[pid].append(dest_ip)
    
    # print out the TCP connections
    for pid in pid_ip_map:
        print("PID: " + str(pid))
        for ip in pid_ip_map[pid]:
            print("\t" + ip)
    
if __name__ == "__main__":
    main()