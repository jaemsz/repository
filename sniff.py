from scapy.all import *
from ctypes import *
import socket
import struct
import psutil

NO_ERROR = 0
ERROR_INSUFFICIENT_BUFFER = 122

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
    
    
def get_process_name(sip, dip, sport, dport):
    windll.iphlpapi.GetTcpTable2.argtypes = [c_void_p, POINTER(c_ulong), c_bool]
    tcp_table_size = c_ulong()
    pid = -1
    
    ret = windll.iphlpapi.GetTcpTable2(None, byref(tcp_table_size), True)
    if ret == ERROR_INSUFFICIENT_BUFFER:
        tcp_table = MIB_TCPTABLE2_FACTORY(tcp_table_size.value)
        
        ret = windll.iphlpapi.GetTcpTable2(byref(tcp_table), byref(tcp_table_size), True)
        if ret != NO_ERROR:
            print("ERROR: GetTcpTable2() failed, error = " + str(ret))
        else:
            for i in range(tcp_table.dwNumEntries):
                pid = tcp_table.table[i].dwOwningPid
                src_ip = socket.inet_ntoa(struct.pack('<L', tcp_table.table[i].dwLocalAddr))
                dst_ip = socket.inet_ntoa(struct.pack('<L', tcp_table.table[i].dwRemoteAddr))
                src_port = socket.ntohs(tcp_table.table[i].dwLocalPort)
                dst_port = socket.ntohs(tcp_table.table[i].dwRemotePort)
                if src_ip == sip and dst_ip == dip and src_port == sport and dst_port == dport:
                    try:
                        return psutil.Process(pid).name(), pid
                    except psutil.NoSuchProcess:
                        return "<UNKNOWN>", pid
    if pid == 4:
        return "System", pid
    else:
        return "<UNKNOWN>", pid
    
def on_packet(pkt):
    protocol = ""
        
    src_port = 0
    dst_port = 0
    if TCP in pkt:
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
        protocol += "TCP,"
    elif UDP in pkt:
        src_port = pkt[UDP].sport
        dst_port = pkt[UDP].dport
        protocol += "UDP,"
    
    name = ""
    if DNS in pkt:
        if pkt.qdcount > 0 and isinstance(pkt.qd, DNSQR):
            name = pkt[DNS].qd.qname
            name = name.decode("utf-8")
            protocol += "DNSQR,"
        elif pkt.ancount > 0 and isinstance(pkt.an, DNSRR):
            name = pkt.an.rdata
            name = name.decode("utf-8")
            protocol += "DNSRR,"

    src_ip = ""
    dst_ip = ""
    if IP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        protocol += "IP"
            
    process_name, pid = get_process_name(src_ip, dst_ip, src_port, dst_port)
    
    print("{:10}{:30}{:6}{:10}{:10}{:20}{:9}{:10}{:10}{:20}{:9}{:10}{:8}{:50}{:8}{:10}".format(
        "PROCESS:", process_name, "PID:", str(pid), 
        "SRC IP:", src_ip, 
        "SPORT:", str(src_port), 
        "DST IP:", dst_ip, 
        "DPORT:", str(dst_port),
        "DNS:", name, 
        "PROT:", protocol))
    
    
def main():
    sniff(filter="ip and tcp and udp and dns", prn=on_packet)
    

if __name__ == "__main__":
    main()