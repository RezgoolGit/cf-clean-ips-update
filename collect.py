import time
import json
import dns
import dns.resolver
from datetime import datetime

def main():
    result = collect()

    with open('list.json', 'w') as json_file:
        json_file.write(json.dumps(result, indent=4))

    with open('list.txt', 'w') as text_file:
        text_file.write(f"Last Update: {result['last_update']}\n\nIPv4:\n")
        for el in result["ipv4"]:
            text_file.write(f"  - {el['ip']:15s}    {el['operator']:5s}    {el['provider']}    {el['created_at']}\n")


def collect():
    result = {
        "last_update": "",
        "last_timestamp": 0,
        "ipv4": [],
        "ipv6": []
    }

    providers = json.load(open('providers.json'))
    try:
        existing_ips = json.load(open('list.json'))
    except FileNotFoundError: 
        existing_ips = {"ipv4": [], "ipv6": []} 
    last_update = 0

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2

    for provider in providers:
        # IPv4
        try:
            ipv4_result = resolver.resolve(provider, "A")
            for ipv4 in ipv4_result:
                ip = ipv4.to_text()
                if ip not in [el["ip"] for el in result["ipv4"]]: 
                    prev = next((el for el in existing_ips["ipv4"] if el["ip"] == ip), None)
                    created_at = prev["created_at"] if prev else int(time.time())
                    last_update = created_at if created_at > last_update else last_update
                    result["ipv4"].append({
                        "ip": ip,
                        "operator": providers[provider],
                        "provider": '.'.join(provider.split('.')[1:]),
                        "created_at": created_at
                    })
        except:
            pass

    # Filter out IPs that are present in the existing_ips file
    new_ipv4 = [el for el in result["ipv4"] if el["ip"] not in [x["ip"] for x in existing_ips["ipv4"]]]
    result["ipv4"] = new_ipv4

    result["last_update"] = datetime.fromtimestamp(last_update).__str__()
    result["last_timestamp"] = last_update

    result["ipv4"].sort(key=lambda el: el["created_at"], reverse=True)
    result["ipv4"].sort(key=lambda el: el["operator"])
    return result

if __name__ == '__main__':
    main()
