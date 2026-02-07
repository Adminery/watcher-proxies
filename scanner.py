import re, json, socket, time, requests, concurrent.futures
from ipaddress import ip_address

# کشورها
TARGET_COUNTRIES = {
    "USA": "US",
    "Germany": "DE",
    "UK": "GB",
    "France": "FR",
    "Netherlands": "NL",
    "Finland": "FI",
    "Sweden": "SE",
    "Turkey": "TR",
    "UAE": "AE",
    "Singapore": "SG",
    "Japan": "JP"
}

# سورس‌های نسبتاً زنده‌تر
SOURCES = [
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/mtproto.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/mtproto.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/mtproto.txt"
]

def tcp_ping(host, port, timeout=2):
    try:
        start = time.time()
        sock = socket.create_connection((host, int(port)), timeout=timeout)
        sock.close()
        return int((time.time() - start) * 1000)
    except:
        return None

def parse_proxy(link):
    try:
        server = re.search(r"server=([^&]+)", link).group(1)
        port = re.search(r"port=([^&]+)", link).group(1)
        secret = re.search(r"secret=([^&]+)", link).group(1)

        ping = tcp_ping(server, port)
        if not ping or ping > 1200:
            return None

        return {
            "server": server,
            "port": port,
            "secret": secret,
            "ping": ping
        }
    except:
        return None

def main():
    print("🚀 Watcher V2 Scan Started")

    raw_links = []
    for src in SOURCES:
        try:
            txt = requests.get(src, timeout=10).text
            raw_links += re.findall(r"tg://proxy\?server=[^\s<>\"']+", txt)
        except:
            pass

    raw_links = list(set(raw_links))
    print(f"📡 Raw MTProto found: {len(raw_links)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as ex:
        results = list(ex.map(parse_proxy, raw_links))

    valid = [r for r in results if r]
    print(f"✅ Valid proxies: {len(valid)}")

    final = {c: [] for c in TARGET_COUNTRIES}

    # چون GeoIP نداریم، فعلاً همه رو تو ALL می‌ریزیم
    for p in sorted(valid, key=lambda x: x["ping"]):
        for country in final:
            if len(final[country]) < 20:
                final[country].append(p)

    with open("proxies.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print("🔥 proxies.json updated")

if __name__ == "__main__":
    main()