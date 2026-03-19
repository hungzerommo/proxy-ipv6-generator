import ipaddress
import random
import os
import subprocess
from core.config import PROXY_CFG

def generate_random_ipv6(base_ip_str):
    try:
        network = ipaddress.IPv6Network(base_ip_str, strict=False)
        start = int(network.network_address)
        end = int(network.broadcast_address)
        
        # Tạo số ngẫu nhiên trong dải
        rand_int = random.randint(start, end)
        return str(ipaddress.IPv6Address(rand_int))
    except Exception as e:
        return None

def write_3proxy_cfg(proxy_list, no_auth, user, password):
    with open(PROXY_CFG, "w", encoding="utf-8") as f:
        f.write("maxconn 500\nnscache 65536\nflush\n\n")
        
        if no_auth:
            f.write("auth none\n")
        else:
            f.write("auth strong\n")
            if user and password:
                f.write(f"users {user}:CL:{password}\n")
                
        f.write("allow *\n\n")
        
        for p in proxy_list:
            if p['in_ip'] == "0.0.0.0":
                f.write(f"proxy -6 -n -a -p{p['port']} -e{p['out_ip']}\n")
            else:
                f.write(f"proxy -6 -n -a -p{p['port']} -i{p['in_ip']} -e{p['out_ip']}\n")
        
        f.write("\nflush\n")

def add_ips_to_interface(interface_name, proxy_list):
    script_file = "add_ips.txt"
    with open(script_file, "w") as f:
        for p in proxy_list:
            f.write(f'interface ipv6 add address interface="{interface_name}" address="{p["out_ip"]}"\n')
            
    proc = subprocess.Popen(f'netsh -f "{script_file}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return proc, script_file
