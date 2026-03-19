import os

# Registry Path for storing settings
REGISTRY_PATH = r"Software\Proxyv6Generator"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(BASE_DIR, "locales")
PROXY_BIN = os.path.join(BASE_DIR, r"3proxy\bin64\3proxy.exe")
if not os.path.exists(PROXY_BIN):
    PROXY_BIN = os.path.join(BASE_DIR, "3proxy.exe")
PROXY_CFG = os.path.join(BASE_DIR, "3proxy.cfg")
LAST_PROXIES_FILE = os.path.join(BASE_DIR, "last_proxies.json")
