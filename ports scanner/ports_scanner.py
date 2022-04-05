import argparse
from socket import *
from concurrent.futures import ThreadPoolExecutor, wait

OPEN = "open"
CLOSED = "closed"


def tcp_scanner(port: int):
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host_name, port))
    except error or timeout:
        result = CLOSED
        return f"{port} is {result}"
    else:
        result = "is open"
        return f"{port} is {result}"
    finally:
        s.close()


def check_correct_ports(l, r):
    if l > 0 and r < 65536:
        return True
    else:
        raise Exception("Invalid range of ports! check help for more information")


def udp_scanner(port: int) -> str:
    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(0.5)
    result = str
    try:
        address = (gethostbyname(host_name), port)
        s.connect(address)
        s.send(bytes(0))
        s.recv(1024)
    except timeout:
        result = OPEN
    except error:
        result = CLOSED
    finally:
        s.close()
    return f"{port} is {result}"


def print_tcp_results(port):
    print(tcp_scanner(port))


def print_udp_results(port):
    print(udp_scanner(port))


def scan_ports(threads_number: int, protocol_type: str, ports_range: str):
    l, r = int(ports_range.split(":")[0]), int(ports_range.split(":")[1])
    if check_correct_ports(l, r):
        if protocol_type == "TCP":
            l, r = int(ports_range.split(":")[0]), int(ports_range.split(":")[1])
            with ThreadPoolExecutor(max_workers=threads_number) as executor:
                wait([executor.submit(print_tcp_results, p) for p in range(l, r + 1)])
        else:
            with ThreadPoolExecutor(max_workers=threads_number) as executor:
                wait([executor.submit(print_udp_results, p) for p in range(l, r + 1)])


def main():
    script_name = "TCP/UDP Scanner"
    scanner = argparse.ArgumentParser(
        usage=f"{script_name} [-a ADDRESS] -t (protocol_type) -r (range_port) [-n THREAD_NUMBER]"
    )
    scanner.add_argument(
        "-a", "--address", default="localhost", type=str, help="Enter a host name for scan"
    )
    scanner.add_argument("-t", "--protocol_type", type=str, help="Type of protocol for scan")
    scanner.add_argument(
        "-r", "--ports_range", type=str, help="range of ports to be checked"
    )
    scanner.add_argument(
        "-n", "--thread_number", default=100, type=int, help="Count of threads to scan"
    )
    args = scanner.parse_args()
    global host_name
    try:
        host_name = gethostbyname(args.address)
    except gaierror:
        raise Exception("Incorrect host name!")
    p_type = args.protocol_type
    p_range = args.ports_range
    threads_number = args.thread_number
    scan_ports(threads_number, p_type, p_range)


if __name__ == "__main__":
    main()
