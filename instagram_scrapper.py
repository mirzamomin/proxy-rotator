"""
    * Entirely Developed by Momin, ASE@NXB
"""

"""
    1. Imports 
"""

import asyncio
import requests
import urllib
import instaloader
from instascrape import Profile
import os

from googleapiclient import discovery
from google.oauth2 import service_account
from proxybroker import Broker
import shutup

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



def insta_scrapper(proxy_pool, usernames, data):
    """
        Used to scrape Instagram features as required

        Parameters
        ----------
        proxy_pool: list
            Pool of valid & working proxies that we can use to scrape instragram 
        usernames: list
            List of Instagram usernames of which the details are to be fetched
    """
    for index, proxy in enumerate(proxy_pool):
        try:

            # Splitting proxy host and port and creating a URL to export to environment variable
            proxy_host = proxy['http'].split(':')[0]
            proxy_port = proxy['http'].split(':')[1]
            proxy_url = f'http://{proxy_host}:{proxy_port}'

            # Setting the proxy environment variable using os.environ
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url

            # Scrapping Instagram using InstaLoader package
            insta = instaloader.Instaloader()
            profile = instaloader.Profile.from_username(insta.context, usernames[index])
            insta.download_profilepic(profile=profile)
            data.append([profile.username, profile.full_name, profile.followers, profile.followees])

            # Scrapping Instagram using instascrape package
            # google = Profile('https://www.instagram.com/mominooooo/')
            # google.scrape()

            # Exporting valid proxies to proxies.txt for record using File Handling
            file = open('proxies.txt', 'a')
            file.write(proxy_url + f'\n')
            file.close()

        except Exception as e:
            print('@@@ ERROR: {}\n {}\n\n'.format(proxy, e))
            print('----------------------------------------------------------------')



def google_sheets_uploader(data):
    """
        Uploads username, full name, followers & followees retrieved from Instagram 
        to Google Sheets using v4 API

        Parameters
        ----------
        data: list
            List of user details like username, full name, followers & followees

    """
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        secret_file = os.path.join(os.getcwd(), "client_secret.json")
        spreadsheet_id = ""
        range_name = ""
        value_input_option = 'RAW'
        credentials = service_account.Credentials.from_service_account_file(
            secret_file, scopes=scope
        )
        service = discovery.build("sheets", "v4", credentials=credentials)

        result = (
            service.spreadsheets()
            .values()
            .append(body={'values': data}, spreadsheetId=spreadsheet_id, range=range_name, valueInputOption=value_input_option)
            .execute()
        )

    except OSError as e:
        print(e)



def main():
   data = []
   usernames = ['mominooooo']

   pool = proxy_refiner()

   insta_scrapper(pool, usernames, data)
   
   if data != []:
    google_sheets_uploader(data)



if __name__ == '__main__':
    shutup.please()
    main()
