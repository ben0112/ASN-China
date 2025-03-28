import requests
from lxml import etree
import time

def initFile():
    with open("usa_asns.txt", "w") as asnFile:
        pass
initFile()

def saveLatestASN():
    url = "https://bgp.he.net/country/US"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    r = requests.get(url = url, headers = headers).text
    tree = etree.HTML(r)
    asns = tree.xpath('//*[@id="asns"]/tbody/tr')
    initFile()
    for asn in asns:
        asnNumber = asn.xpath('td[1]/a')[0].text.replace('AS','')
        asnName = asn.xpath('td[2]')[0].text
        if asnName != None:
            asnInfo = "{}".format(asnNumber)
            with open("usa_asns.txt", "a") as asnFile:
                asnFile.write(asnInfo)
                asnFile.write("\n")

saveLatestASN()
