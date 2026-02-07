import requests, re, json, socket, time, concurrent.futures

TARGET_COUNTRIES = {
    "USA":"US","Germany":"DE","UK":"GB","France":"FR","Finland":"FI",
    "Netherlands":"NL","Canada":"CA","Singapore":"SG","Japan":"JP","Norway":"NO",
    "Sweden":"SE","Italy":"IT","Spain":"ES","Poland":"PL","Austria":"AT",
    "Switzerland":"CH","Turkey":"TR","UAE":"AE","Qatar":"QA","India":"IN"
}

SOURCES = [
    "https://raw.githubusercontent.com/ALIILAPRO/Proxy/main/mtproto.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/mtproto.txt",
    "https://raw.githubusercontent.com/General_Proxies/Proxy-List/main/MTProto.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/MTProto_RAW.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/mtproto.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/mtproto.txt"
]

def tcp_ping(ip, port):
    times = []
    for _ in range(2):
        try:
            s = time.time()
            sock = socket.create_connection((ip, int(port)), timeout=2)
            sock.close()
            times.append((time.time() - s) * 1000)
        except:
            return None
    return int(sum(times)/len(times))

def get_cc(ip):
    try:
        r = requests.get(f"https://ipwho.is/{ip}", timeout=3).json()
        return r["country_code"] if r["success"] else None
    except:
        return None

def parse(link):
    try:
        server = re.search(r"server=([^&]+)", link).group(1)
        port   = re.search(r"port=([^&]+)", link).group(1)
        secret = re.search(r"secret=([^&]+)", link).group(1)

        ping = tcp_ping(server, port)
        if not ping or ping > 900:
            return None

        cc = get_cc(server)
        if not cc:
            return None

        score = ping
        return {
            "server": server,
            "port": port,
            "secret": secret,
            "ping": ping,
            "score": score,
            "cc": cc
        }
    except:
        return None

def main():
    print("🚀 WATCHER ULTIMATE SCAN STARTED")

    raw = []
    for src in SOURCES:
        try:
            raw += re.findall(r"tg://proxy\?server=[^\s<>\"']+", requests.get(src, timeout=10).text)
        except:
            pass

    raw = list(set(raw))
    print(f"📡 {len(raw)} raw proxies found")

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as ex:
        results = list(ex.map(parse, raw))

    valid = [r for r in results if r]

    final = {c:[] for c in TARGET_COUNTRIES}
    for name, code in TARGET_COUNTRIES.items():
        nodes = [n for n in valid if n["cc"] == code]
        nodes.sort(key=lambda x: x["score"])
        final[name] = nodes[:40]

    with open("proxies.json","w",encoding="utf-8") as f:
        json.dump(final,f,indent=2,ensure_ascii=False)

    print("✅ proxies.json updated successfully")

if __name__ == "__main__":
    main()