# proxy-rotator
A Python proxy rotator, that rotates free pool IPs and can be used for any other scraping purpose.
Uses ProxyBroker to gather free proxies and verifies it against apify.org and filters the expired proxies and finally returns an array of proxies.
Using os python package, the script also swtiches the proxies on the system. Any scrapping logic can be used after the os command.
