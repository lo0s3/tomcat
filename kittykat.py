#!/usr/bin/python3

import os, argparse, requests, gevent.monkey
from base64 import b64encode

from gevent.pool import Pool
gevent.monkey.patch_socket()
requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser(description="Tomcat weak credential scanner. Requires file with credentials on seperate lines (ex: tomcat:s3cret, etc.) and hosts file (ip list).")
parser.add_argument('-c', dest='creds', required=True, metavar="{creds list}")
parser.add_argument('-i', dest='hosts', required=True, metavar="{ip list}")
parser.add_argument('-t', dest="threads", required=True, type=int, default=16, metavar="{thread count}")

args = parser.parse_args()

def check_creds(creds, hosts, threads):
    def fetch(cred, host):
        try:
            headers = { "Authorization": "Basic " + b64encode(cred.encode('utf-8')).decode('utf-8') }
            response = requests.get("http://" + host + ":8080/manager/html", headers=headers, timeout=5, verify=False)

            if response.status_code == 200:
                print(host + " [" + cred + "] ") # weak tomcat creds found

        except Exception as e:
            pass

    pool = Pool(nthreads)

    for cred in creds:
        for host in hosts:
            pool.spawn(fetch, cred, host)
    pool.join()

if __name__ == "__main__":
    file_creds = args.creds
    nthreads = args.threads
    file_hosts = args.hosts

    userpass = [line.strip() for line in open(file_creds, ).readlines()]
    hostnames = [line.strip() for line in open(file_hosts, ).readlines()]

    check_creds(userpass, hostnames, nthreads)
