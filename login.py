'''
LOGIN    = "admin"
PASSWORD = "ciscopsdt"
URL      = "https://sandboxapicdc.cisco.com"

'''

import requests, json, sys
import socket

requests.packages.urllib3.disable_warnings()

apic_ip ='10.103.23.10'
username = 'admin'
#f = open('credentials', 'r')
#switchpassword = f.readline()
password = 'Avpnmw3wl!'


apic_ip = socket.gethostbyname(apic_ip)


#=======================================================================

def add_nodes(apic_ip, s):
    
    print('Trying to register devices...')
    
    myheaders={'content-type':'text/xml'}
    
    url = 'https://' + apic_ip + '/api/node/mo/uni/controller.xml'
    
    myheaders={'content-type':'application/json-rpc'}
    
    payload = '<fabricNodeIdentPol>\n\t<fabricNodeIdentP serial=\"SAL1918E7YZ\" name=\"leaf-1\" nodeId=\"101\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7AB\" name=\"leaf-2\" nodeId=\"102\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7CD\" name=\"leaf-3\" nodeId=\"103\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7EF\" name=\"spine-1\" nodeId=\"201\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7GH\" name=\"spine-2\" nodeId=\"202\"/>\n</fabricNodeIdentPol>'
    
    r = s.post(url, data=payload, verify=False, headers={"Accept": "application/json"})
    
    print(r.text)

#=======================================================================

def del_nodes(apic_ip, s):

    print('Trying to remove devices...')

    url = 'https://' + apic_ip + '/api/node/mo/uni/fabric/outofsvc.json'
    
    payload = "{\"fabricRsDecommissionNode\":\n\t{\"attributes\":\n\t\t{\"tDn\":\"topology/pod-1/node-102\",\n\t\t\"status\":\"created,modified\",\n\t\t\"removeFromController\":\"true\"\n\t\t},\n\t\"children\":[]\n\t}\n}"
    #payload = '{"fabricRsDecommissionNode":{"attributes":{"tDn":"topology/pod-1/node-101","status":"created,modified","removeFromController":"true"},"children":[]}}'
    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache"
        }
    
    response = s.post(url, data=payload, headers=headers)
    
    print(response.text)

#=======================================================================

url = 'https://' + apic_ip + '/api/aaaLogin.json'
print('Loggin into {} with username {}'.format(apic_ip, username))

payload = '{"aaaUser": {"attributes": {"name": "admin","pwd": "Avpnmw3wl!"}}}'
s = requests.Session()
r = s.post(url, data=payload, verify=False, headers={"Accept": "application/json"})

status = r.status_code
cookies = r.cookies
apicCookie = r.cookies

#print('URL: ', url)
print('Response: ', r)

del_nodes(apic_ip, s)





