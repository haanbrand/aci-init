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
file_name = 'nodes_to_del.xlsx'



def get_node_info(file_name):
    print('Trying to get node info...')

    book = xlrd.open_workbook(file_name)
    xl_sheet = book.sheet_by_index(0)
    num_rows=xl_sheet.nrows
    '''node-num,node-name,serial'''
    nodes_list = []
    for row in range(1, num_rows):
        node_num = str(xl_sheet.cell(row,0).value)
        nodes_list.append(node_num)
    
    print('Following are the nodes to be deleted on APIC ({}):'.format(apic_ip))
    print(json.dumps(nodes_list, indent=4, sort_keys=True))
    while True:
        answer = raw_input('Is the above correct? (y/Y/n/N)').lower()
        if answer == 'y':
            return nodes_list
        elif answer == 'n':
            print('Please fix the spreadsheet with correct data')
            print('Exiting...')
            exit()
        else:
            print("Please enter 'y' or 'Y' or 'n' or 'N'")
    return nodes_list


#=======================================================================

def del_nodes(apic_ip, s, nodes_list):

    print('Trying to remove devices...')

    url = 'https://' + apic_ip + '/api/node/mo/uni/fabric/outofsvc.json'
    
    for node in nodes_list:
        print('Removing node id:{}'.format(str(node)))
        payload = '{\"fabricRsDecommissionNode\":\n\t{\"attributes\":\n\t\t{\"tDn\":\"topology/pod-1/node-'+str(node)+'\",\n\t\t\"status\":\"created,modified\",\n\t\t\"removeFromController\":\"true\"\n\t\t},\n\t\"children\":[]\n\t}\n}'
        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"
            }
        response = s.post(url, data=payload, headers=headers)
        print(response.text)
        status = str(response.status_code)
        if status == '200':
            print('success...')
        else:
            print('there was an issue with {} as we got code {}'.format(str(node), status))

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

nodes_list = get_node_info(file_name)
session = login_apic(apic_ip, username, password)
del_nodes(apic_ip, session, nodes_list)





