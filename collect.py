import time
import json
import dns
import dns.resolver
from datetime import datetime

def collect_dns_records(providers):
    """
    Collect DNS records for the given providers.
    """
    result = set()  # Use a set to store unique IPs
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2

    for provider in providers:
        try:
            ipv4_result = resolver.resolve(provider, "A")
            for ipv4 in ipv4_result:
                ip = ipv4.to_text()
                result.add(ip)  # Add IP to the set
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            pass

    return result

def load_existing_ips(filename):
    """
    Load existing IPs from a JSON file.
    """
    try:
        with open(filename, 'r') as json_file:
            existing_ips = json.load(json_file)
            return existing_ips["ipv4"]
    except FileNotFoundError:
        return []

def save_ips(filename, ips):
    """
    Save IPs to a JSON file.
    """
    with open(filename, 'w') as json_file:
        json_file.write(json.dumps({"ipv4": ips}, indent=4))

def main():
    providers = json.load(open('providers.json'))
    providers = {k: v for k, v in providers.items() if v is not None}  # Remove providers with no value
    existing_ips = load_existing_ips('list.json')
    new_ips = collect_dns_records(providers.keys())

    # Remove existing IPs from the new list
    new_ips = [ip for ip in new_ips if ip not in [e['ip'] for e in existing_ips]]

    # Create a list of dictionaries with IP, operator, provider, and created_at
    new_ips_list = []
    for ip in new_ips:
        for provider, operator in providers.items():
            if ip in [i for i in dns.resolver.resolve(provider, 'A')]:
                new_ips_list.append({
                    "ip": ip,
                    "operator": operator,
                    "provider": '.'.join(provider.split('.')[1:]),
                    "created_at": int(time.time())
                })

    # Save the new IPs to the JSON file
    save_ips('list.json', new_ips_list)

    # Save the new IPs to the text file
    with open('list.txt', 'w') as text_file:
        text_file.write(f"Last Update: {datetime.now().__str__()}\n\nIPv4:\n")
        for el in new_ips_list:
            text_file.write(f"  - {el['ip']:15s}    {el['operator']:5s}    {el['provider']}    {el['created_at']}\n")

if __name__ == '__main__':
    main()
