import socket
import struct
from urllib.error import URLError, HTTPError
import urllib.request
import json
import argparse


def get_echo_request():
    temp_header = struct.pack("bbHHh", 8, 0, 0, 0, 0)
    checksum = calculate_checksum(temp_header)
    main_header = struct.pack("bbHHh", 8, 0, checksum, 0, 0)
    return main_header


def traceroute(host, timeout, hops):
    try:
        dest = socket.gethostbyname(host)
    except socket.gaierror:
        raise Exception("Не удалось разрешить имя хоста")
    ttl = 1
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(timeout)
    echo_request = get_echo_request()
    addr = None
    while ttl < hops and addr != dest:
        sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        sock.sendto(echo_request, (dest, 33434))
        try:
            packet, addr = sock.recvfrom(1024)
            if addr[0]:
                addr = addr[0]
                message = get_info(addr, ttl)
                print(message)
        except socket.timeout:
            print("*****")
        ttl += 1
    sock.close()


def calculate_checksum(packet):
    checksum = 0
    for i in range(0, len(packet), 2):
        word = packet[i] + (packet[i + 1] << 8)
        checksum = checksum + word
        overflow = checksum >> 16
        while overflow > 0:
            checksum = checksum & 0xFFFF
            checksum = checksum + overflow
            overflow = checksum >> 16
    overflow = checksum >> 16
    while overflow > 0:
        checksum = checksum & 0xFFFF
        checksum = checksum + overflow
        overflow = checksum >> 16
    checksum = ~checksum
    checksum = checksum & 0xFFFF
    return checksum


def get_info(ip, ttl):
    country, provider = ("--", "--")
    link = "https://stat.ripe.net/data/whois/data.json?resource=" + ip
    try:
        with urllib.request.urlopen(link) as page:
            data = json.loads(page.read().decode("utf-8"))["data"]
    except (URLError, HTTPError) as err:
        return country, provider
    for record in data["records"]:
        for item in record:
            if item["key"].lower() == "country" and country == "--":
                country = item["value"]
    as_number = None
    for record in data["irr_records"]:
        if country != "--" and provider != "--":
            break
        for item in record:
            if item["key"] == "origin":
                as_number = item["value"]
            if item["key"] == "descr" and provider == "--":
                provider = item["value"]
    try:
        message = "{:<3}\t{:<15}\tAS{:<6}\t{:<4}\t{:<30}".format(
            ttl, ip, as_number, country, provider
        )
    except Exception:
        message = "{:<3}\t{:<15}".format(ttl, ip)
    return message


def main():
    script_name = "Traceroute"
    scanner = argparse.ArgumentParser(
        usage=f"{script_name} -a ADDRESS [-t TIMEOUT] [-h MAX_HOPS]"
    )
    scanner.add_argument(
        "-a", "--address", type=str, help="Enter a hostname for traceroute"
    )
    scanner.add_argument("-t", "--timeout", default=2, type=int, help="Response waiting time")
    scanner.add_argument(
         "--hops", default=30, type=int, help="Maximum number of hops"
    )
    args = scanner.parse_args()
    addr = args.address
    timeout = args.timeout
    hops = args.hops
    traceroute(addr, timeout, hops)


if __name__ == "__main__":
    main()
