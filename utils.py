import re

def parse_ip_port(text):
    # Проверяет формат ip:port или domain:port
    pattern = r'^([a-zA-Z0-9.-]+):(\d+)$'
    match = re.match(pattern, text.strip())
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def is_valid_port(port):
    return 1 <= port <= 65535
