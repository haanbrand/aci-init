'''
LOGIN    = "admin"
PASSWORD = "ciscopsdt"
URL      = "https://sandboxapicdc.cisco.com"

'''

import requests, json, sys, xlrd
#import socket

requests.packages.urllib3.disable_warnings()

apic_ip ='10.103.23.10'
username = 'admin'
#f = open('credentials', 'r')
#switchpassword = f.readline()
password = 'Avpnmw3wl!'
#CSV File name
file_name = 'nodes_to_add.xlsx'



def get_node_info(file_name):
    print('Trying to get node info...')

    book = xlrd.open_workbook(file_name)
    xl_sheet = book.sheet_by_index(0)
    num_rows=xl_sheet.nrows
    '''node-num,node-name,serial'''
    nodes = {}
    nodes_list = []
    for row in range(1, num_rows):
        node_info = {}
        node_num = str(xl_sheet.cell(row,0).value)
        node_name = str(xl_sheet.cell(row,1).value)
        node_serial = str(xl_sheet.cell(row,2).value)
        node_info = { 'name' : node_name, 'nr' : node_num, 'serial' : node_serial}
        nodes_list.append(node_info)
    nodes['nodes'] = nodes_list
    print('Following are the nodes to add on APIC ({}):'.format(apic_ip))
    print(json.dumps(nodes, indent=4, sort_keys=True))
    while True:
        answer = raw_input('Is the above correct? (y/Y/n/N)').lower()
        if answer == 'y':
            return nodes
        elif answer == 'n':
            print('Please fix the spreadsheet with correct data')
            print('Exiting...')
            exit()
        else:
            print("Please enter 'y' or 'Y' or 'n' or 'N'")
    return nodes

#=======================================================================

def add_nodes(apic_ip, session, nodes_dict):
    
    print('Trying to register devices...')
    myheaders={'content-type':'text/xml'}
    url = 'https://' + apic_ip + '/api/node/mo/uni/controller.xml'
    myheaders={'content-type':'application/json-rpc'}
    
    for item in nodes_dict['nodes']:
        print('Adding {}'.format(item['name']))
        #{'nr': '101', 'name': 'leaf-1', 'serial': 'SAL1918E7YZ'}
        #payload = '<fabricNodeIdentPol>\n\t<fabricNodeIdentP serial=\"SAL1918E7YZ\" name=\"leaf-1\" nodeId=\"101\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7AB\" name=\"leaf-2\" nodeId=\"102\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7CD\" name=\"leaf-3\" nodeId=\"103\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7EF\" name=\"spine-1\" nodeId=\"201\"/>\n\t<fabricNodeIdentP serial=\"SAL1918E7GH\" name=\"spine-2\" nodeId=\"202\"/>\n</fabricNodeIdentPol>'
        payload = '<fabricNodeIdentPol>\n\t<fabricNodeIdentP serial=\"' + str(item['serial']) + '\" name=\"' + str(item['name']) + '\" nodeId=\"' + str(item['nr']) + '\"/>\n</fabricNodeIdentPol>'
        r = session.post(url, data=payload, verify=False, headers={"Accept": "application/json"})
        print(r.text)
        status = str(r.status_code)
        if status == '200':
            print('success...')
        else:
            print('there was an issue with {} as we got code {}'.format(str(item['name']), status))

#=======================================================================

def login_apic(apic_ip, username, password):
    print('Logging into {} with username {}'.format(apic_ip, username))
    url = 'https://' + apic_ip + '/api/aaaLogin.json'
    payload = '{"aaaUser": {"attributes": {"name": "' + username + '","pwd": "' + password + '"}}}'

    session = requests.Session()
    r = session.post(url, data=payload, verify=False, headers={"Accept": "application/json"})
    
    status = str(r.status_code)
    cookies = r.cookies
    apicCookie = r.cookies
    
    if status == '200':
        print('successfully logged in...')
    else:
        exit()
    return session

#=============MAIN Start==========================================================

nodes_dict = get_node_info(file_name)
session = login_apic(apic_ip, username, password)
add_nodes(apic_ip, session, nodes_dict)





