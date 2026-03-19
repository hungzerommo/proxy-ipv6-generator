import os
import subprocess
import winreg as reg
from core.config import REGISTRY_PATH, PROXY_BIN

def get_network_interfaces():
    try:
        cmd = "powershell \"Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -ExpandProperty Name\""
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return [line.strip() for line in proc.stdout.split('\n') if line.strip()]
    except Exception as e:
        print(f"Error getting interfaces: {e}")
        return []

def get_ipv6_addresses(interface_name):
    try:
        cmd = f"powershell \"Get-NetIPAddress -InterfaceAlias '{interface_name}' -AddressFamily IPv6 | Select-Object -ExpandProperty IPAddress\""
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        ips = [ip.strip() for ip in proc.stdout.split('\n') if ip.strip()]
        return [ip for ip in ips if not ip.startswith("fe80")]
    except Exception as e:
        print(f"Error getting IPv6 array: {e}")
        return []

def check_win_startup():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_READ)
        value, _ = reg.QueryValueEx(key, "Proxyv6Generator")
        reg.CloseKey(key)
        return True
    except WindowsError:
        return False

def set_win_startup(enable, script_path):
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
        if enable:
            reg.SetValueEx(key, "Proxyv6Generator", 0, reg.REG_SZ, f'"{script_path}"')
        else:
            try:
                reg.DeleteValue(key, "Proxyv6Generator")
            except FileNotFoundError:
                pass
        reg.CloseKey(key)
    except Exception as e:
        print(f"Startup toggle error: {e}")

def kill_3proxy():
    cmd = "taskkill /F /IM 3proxy.exe /T"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

def open_firewall():
    if os.path.exists(PROXY_BIN):
        cmd = f'netsh advfirewall firewall add rule name="3Proxy" dir=in action=allow program="{PROXY_BIN}" enable=yes'
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    return None

def clean_ipv6(interface_name, base_ip):
    # This generates a netsh script to clean IPs
    cmd = f"powershell \"Get-NetIPAddress -InterfaceAlias '{interface_name}' -AddressFamily IPv6 | Where-Object {{ $_.IPAddress -notmatch '^fe80' -and $_.IPAddress -ne '{base_ip}' }} | Select-Object -ExpandProperty IPAddress\""
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    ips_to_remove = [ip.strip() for ip in proc.stdout.split('\n') if ip.strip()]
    
    if ips_to_remove:
        script_file = "tool_del_ips.txt"
        with open(script_file, "w") as f:
            for ip in ips_to_remove:
                f.write(f'interface ipv6 delete address interface="{interface_name}" address="{ip}"\n')
        
        proc2 = subprocess.Popen(f'netsh -f "{script_file}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        proc2.wait()
        try: os.remove(script_file)
        except: pass
    return len(ips_to_remove)
