import socket
import urllib.request
import time
import psutil

def check_one_proxy(port, use_auth=False, user="", pwd=""):
    """Check 1 proxy, trả về True/False. Không chạm UI."""
    proxy_ip = "127.0.0.1"
    
    # Bước 1: Socket check nhanh
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((proxy_ip, port))
        sock.close()
        if result != 0:
            return False
    except Exception:
        return False
    
    # Bước 2: HTTP check với fallback
    test_urls = [
        'http://httpbin.org/ip',
        'http://ip-api.com/json',
        'http://icanhazip.com',
    ]
    
    proxy_handler = urllib.request.ProxyHandler({
        'http': f'http://{proxy_ip}:{port}',
        'https': f'http://{proxy_ip}:{port}',
    })
    
    if use_auth and user:
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, f'http://{proxy_ip}:{port}', user, pwd)
        auth_handler = urllib.request.ProxyBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(proxy_handler, auth_handler)
    else:
        opener = urllib.request.build_opener(proxy_handler)
    
    for url in test_urls:
        try:
            resp = opener.open(url, timeout=10)
            if resp.status == 200:
                return True
        except Exception:
            continue
    
    return True  # Port mở nhưng HTTP fail → vẫn coi là sống

def count_connections_sync(ports):
    """Đếm kết nối TCP của psutil cho list port, trả về dictionary."""
    port_set = set(ports)
    port_count = {port: 0 for port in port_set}
    total_connections = 0
    
    try:
        connections = psutil.net_connections(kind='tcp')
        for conn in connections:
            if conn.laddr and conn.laddr.port in port_set:
                if conn.status == 'ESTABLISHED':
                    port_count[conn.laddr.port] += 1
                    total_connections += 1
    except Exception as e:
        print(f"Error psutil: {e}")
        pass
        
    return port_count, total_connections
