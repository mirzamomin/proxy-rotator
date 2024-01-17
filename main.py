"""
    * Entirely Developed by Momin, SE@NXB
"""

"""
    1. Imports 
"""

import os
import sys
import shutup
import asyncio
import requests
import argparse

if sys.platform == 'win32':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

parser = argparse.ArgumentParser(description='Free proxies fetcher and rotator to scrape websites')
parser.add_argument('limit',help="Number of Proxies to Fetch")
args=parser.parse_args()

limit = int(args.limit)

from proxybroker import Broker


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
        broker.find(types=['HTTP', 'HTTPS'], limit=limit),
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


def export(proxy_pool):
    """
        Used to scrape Instagram features as required

        Parameters
        ----------
        proxy_pool: list
            Pool of valid & working proxies that we can use to scrape instragram 
    """
    for proxy in proxy_pool:
        try:

            # Splitting proxy host and port and creating a URL to export to environment variable
            proxy_host = proxy['http'].split(':')[0]
            proxy_port = proxy['http'].split(':')[1]
            proxy_url = f'http://{proxy_host}:{proxy_port}'

            # Setting the proxy environment variable using os.environ
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url

            ### USE YOUR SCRAPPING LOGIC HERE ###

            # Exporting valid proxies to proxies.txt for record using File Handling
            file = open('proxies.txt', 'a')
            file.write(proxy_url + f'\n')
            file.close()

        except Exception as e:
            print('@@@ ERROR: {}\n {}\n\n'.format(proxy, e))
            print('----------------------------------------------------------------')


def main():
    proxy_pool = proxy_refiner()
    export(proxy_pool)


if __name__ == '__main__':
    shutup.please()
    main()
