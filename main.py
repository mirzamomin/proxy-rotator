"""
    * Entirely Developed by Momin, SE@NXB
"""

"""
    1. Imports 
"""

import shutup
import asyncio
import requests

from proxybroker import Broker
from googleapiclient import discovery
from google.oauth2 import service_account

"""
    2. Main Functionality
"""

async def append_proxies(proxies, proxy_pool): # async function (coroutine function) to fetch and append proxies
    """
        Fetches the proxies from ProxyBroker and appends them to a proxy pool.

        Parameters
        ----------
        proxies:

        proxy_pool:
            An empty array in which the proxies are appended

        Returns
        -------
            None

    """
    while True:
        proxy = await proxies.get() # await command used to get proxies asynchronously
        if proxy is None: break # if proxy not found, break out of the while loop
        if 'HTTPS' and 'HTTPS' in proxy.expected_types: # filter out proxies that have both HTTP and HTTPS
            proxy_pool.append({ # append the proxy to the pool of proxies that will be used to scrape Instagram
                "http": "{0}:{1}".format(proxy.host, proxy.port),
                "https": "{0}:{1}".format(proxy.host, proxy.port)
                })
            

            
def proxy_refiner():
    """
        Calls append_proxies() asynchronously, refines the proxies returned that don't function and
        cross-checks the IPs with ipify.org

        Returns
        -------
        proxy_pool: list
            Pool of valid & working proxies that we can use to scrape instragram
    """
    proxy_pool = []
    url = 'https://api.ipify.org'
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(
        broker.find(types=['HTTP', 'HTTPS'], limit=10),
        append_proxies(proxies, proxy_pool))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)

    for proxy in proxy_pool:
        session = requests.Session()
        session.proxies = proxy

        try:
            session.get(url)
        except:
            proxy_pool.remove(proxy)
    return proxy_pool


def main():
    print(proxy_refiner())


if __name__ == '__main__':
    shutup.please()
    main()
