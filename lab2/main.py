#!/usr/bin/env python3

import argparse
import platform
import re
import subprocess

def check_icmp_enable():
    with open("/proc/sys/net/ipv4/icmp_echo_ignore_all", "r") as f:
        if f.read().strip() != "0":
            raise RuntimeError("ICMP disabled")

def is_match(regexp, phrase):
    return re.compile(regexp).match(phrase)

def is_ip_address(ip):
    # https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address/106223#106223
    ip_regexp = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    return is_match(ip_regexp, ip)

def is_host_name(host_name):
    # https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address/106223#106223
    host_name_regexp = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    return is_match(host_name_regexp, host_name)

def check_host(host):
    if not is_ip_address(host) and not is_host_name(host):
        raise RuntimeError("Incorrect host")

def run_command(command):
    result = subprocess.run(command, stderr = subprocess.DEVNULL, stdout = subprocess.DEVNULL)
    return result.returncode

def generate_command(host, size):
    size = str(size)
    os = platform.system().lower()
    match os:
        case "darwin":
            return f"ping -D -s {size} -c 1 {host}".split()
        case "linux":
            return f"ping -M do -s {size} -c 1 {host}".split()
        case "windows":
            return f"ping -M do -s {size} -n 1 {host}".split()
        case _:
            raise RuntimeError("Unknown os")

def can_ping(host, size):
    command = generate_command(host, size)
    returncode = run_command(command)
    if not returncode in [0, 1]:
        raise RuntimeError(f"Incorrect return code in check for size = {size}")
    return returncode == 0

def find_mtu(host):
    if not can_ping(host, 0):
        raise RuntimeError(f"Destination is not reachable")

    L = 0
    R = 1502 - 28

    while L < R - 1:
        M = (L + R) // 2
        if can_ping(host, M):
            L = M
        else:
            R = M

    return L + 28

if __name__ == "__main__":
    try:
        check_icmp_enable()

        parser = argparse.ArgumentParser()
        parser.add_argument('--host', required = True, help = 'explored destination')

        args = parser.parse_args()
        host = args.host

        check_host(host)

        MTU = find_mtu(host)
        print(f"MTU = {MTU}")
    except Exception as e:
        print("Failed with an exception")
        print(e)