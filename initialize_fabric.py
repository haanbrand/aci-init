'''
LOGIN    = "admin"
PASSWORD = "ciscopsdt"
URL      = "https://sandboxapicdc.cisco.com"

'''

import requests, json, sys, xlrd, os
#import socket

requests.packages.urllib3.disable_warnings()

apic_ip ='10.103.23.10'
username = 'admin'
#f = open('credentials', 'r')
#switchpassword = f.readline()
password = 'Avpnmw3wl!'
#Excel File name
file_name = 'fabric_init.xlsx'

def start_msg(apic_ip):
    msg = '''
    ***This will initialize the fabric on APIC with IP: {apic} ***
    
    Make sure the spreadsheet "fabric_init.xlsx" is populated correctly...
    
    In each section before config will be applied the always present 
    "Yes/No" to proceed question will be asked...
    
    Have fun.
    
    '''
    print(msg.format(apic = apic_ip))
    try:
        input("Press enter to continue")
    except SyntaxError:
        pass

def get_node_info(file_name):
    os.system('cls||clear')
    print('\n\n\nGetting node info from {}'.format(file_name))

    book = xlrd.open_workbook(file_name)
    xl_sheet = book.sheet_by_name('nodes_to_add')
    num_rows=xl_sheet.nrows
    nodes = {}
    nodes_list = []
    for row in range(1, num_rows):
        node_info = {}
        node_num = str(xl_sheet.cell(row,0).value)
        node_name = str(xl_sheet.cell(row,1).value)
        node_serial = str(xl_sheet.cell(row,2).value)
        node_oob_addr = str(xl_sheet.cell(row,3).value)
        node_oob_mask = str(xl_sheet.cell(row,4).value)
        node_oob_ip = node_oob_addr + '/' + node_oob_mask
        node_oob_gwy = str(xl_sheet.cell(row,5).value)
        node_info = { 'name' : node_name, 'nr' : node_num, 'serial' : node_serial, 'oob_ip' : node_oob_ip, 'oob_gwy' : node_oob_gwy}
        nodes_list.append(node_info)
    nodes['nodes'] = nodes_list
    print('Following are the nodes to add on APIC ({}):\n'.format(apic_ip))
    #print(json.dumps(nodes, indent=4, sort_keys=True))
    for node in nodes_list:
        print('Node name: {} - Node id: {} - Node S/N: {}\nOOB mgmt info (IP/Mask/Gwy): {}/{}\n'.format(node['name'], node['nr'],node['serial'],node['oob_ip'],node['oob_gwy']))
    
    while True:
        answer = raw_input('\nIs the above correct? (y/Y/n/N)').lower()
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
    #myheaders ={'content-type':'text/xml'}
    url = 'https://' + apic_ip + '/api/node/mo/uni/controller.xml'
    #myheaders ={'content-type':'application/json-rpc'}
    
    for item in nodes_dict['nodes']:
        print('Adding {}'.format(item['name']))
        #{'nr': '101', 'name': 'leaf-1', 'serial': 'SAL1918E7YZ'}
        payload = '<fabricNodeIdentPol>\n\t<fabricNodeIdentP serial=\"' + str(item['serial']) + '\" name=\"' + str(item['name']) + '\" nodeId=\"' + str(item['nr']) + '\"/>\n</fabricNodeIdentPol>'
        r = session.post(url, data=payload, verify=False, headers={"Accept": "application/json"})
        #print(r.text)
        status = str(r.status_code)
        if status == '200':
            print('success...')
        else:
            print('there was an issue with {} as we got code {}'.format(str(item['name']), status))
            
    # adding OOB MGMT info
    for item in nodes_dict['nodes']:
        print('Creating OOB mgmt for {}'.format(item['name']))
        #headers = {'Content-Type': "application/json",'Cache-Control': "no-cache"}
        url = 'https://' + apic_ip + '/api/node/mo/uni/tn-mgmt/mgmtp-default/oob-default/rsooBStNode-[topology/pod-1/node-'+str(item['nr'])+'].json'
        payload = '{"mgmtRsOoBStNode":{"attributes":{"tDn":"topology/pod-1/node-'+str(item['nr'])+'","addr":"'+str(item['oob_ip'])+'","gw":"'+str(item['oob_gwy'])+'","status":"created"},"children":[]}}'
        r = session.post(url, data=payload, verify=False, headers={"Accept": "application/json"})
        check_response(r)
            
            
    # adding user nexio
    headers = {'Content-Type': "application/json",'Cache-Control': "no-cache"}
    url = 'https://'+apic_ip+'/api/node/mo/uni/userext/user-nexio.json'
    payload = '{"aaaUser":{"attributes":{"dn":"uni/userext/user-nexio","name":"nexio","pwd":"Samba321","firstName":"Nexio","lastName":"Support","phone":"555-1111","email":"jan@wilkens.com","rn":"user-nexio","status":"created"},"children":[{"aaaUserDomain":{"attributes":{"dn":"uni/userext/user-nexio/userdomain-all","name":"all","status":"created,modified"},"children":[{"aaaUserRole":{"attributes":{"dn":"uni/userext/user-nexio/userdomain-all/role-admin","name":"admin","privType":"writePriv","status":"created,modified"},"children":[]}}]}}]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)

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
        print('\n***** successfully logged in...*****')
    else:
        exit()
    return session

#=======================================================================
def add_intf_pols(apic_ip, session):
    #This will add all the usual interface policies which is normally used
    print('\nWe will now try and add the usual Interface Policies...')
    while True:
        answer = raw_input('\nDo you want to continue? (y/Y/n/N)').lower()
        if answer == 'y':
            break
        elif answer == 'n':
            print('Exiting...')
            exit()
        else:
            print("Please enter 'y' or 'Y' or 'n' or 'N'")
            
            
    headers = {'Content-Type': "application/json",'Cache-Control': "no-cache"}
    print('\n====================Creating Interface policies====================')
    #=====CDP Policies=====
    print('**********Creating CDP_OFF policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/cdpIfP-CDP_OFF.json'
    payload = '{"cdpIfPol":{"attributes":{"adminSt":"disabled","dn":"uni/infra/cdpIfP-CDP_OFF","name":"CDP_OFF","rn":"cdpIfP-CDP_OFF","status":"created"}}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)
    
    print('\n**********Creating CDP_ON policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/cdpIfP-CDP_ON.json'
    payload = '{"cdpIfPol":{"attributes":{"adminSt":"enabled","dn":"uni/infra/cdpIfP-CDP_ON","name":"CDP_ON","rn":"cdpIfP-CDP_ON","status":"created"}}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)
        
    #=====Link Level Policies=====
    print('\n**********Creating 1Gbps_autoNeg_ON policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/hintfpol-1Gbps_autoNeg_ON.json'
    payload = '{"fabricHIfPol":{"attributes":{"dn":"uni/infra/hintfpol-1Gbps_autoNeg_ON","name":"1Gbps_autoNeg_ON","speed":"1G","rn":"hintfpol-1Gbps_autoNeg_ON","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)

    print('\n**********Creating 1Gbps_autoNeg_OFF policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/hintfpol-1Gbps_autoNeg_OFF.json'
    payload = '{"fabricHIfPol":{"attributes":{"dn":"uni/infra/hintfpol-1Gbps_autoNeg_OFF","autoNeg":"off","name":"1Gbps_autoNeg_OFF","speed":"1G","rn":"hintfpol-1Gbps_autoNeg_OFF","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)

    print('\n**********Creating 10Gbps_autoNeg_ON policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/hintfpol-10Gbps_autoNeg_ON.json'
    payload = '{"fabricHIfPol":{"attributes":{"annotation":"","autoNeg":"on","descr":"","dn":"uni/infra/hintfpol-10Gbps_autoNeg_ON","fecMode":"inherit","linkDebounce":"100","name":"10Gbps_autoNeg_ON","nameAlias":"","ownerKey":"","ownerTag":"","speed":"10G"}}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)

    print('\n**********Creating 10Gbps_autoNeg_OFF policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/hintfpol-10Gbps_autoNeg_OFF.json'
    payload = '{"fabricHIfPol":{"attributes":{"annotation":"","autoNeg":"off","descr":"","dn":"uni/infra/hintfpol-10Gbps_autoNeg_OFF","fecMode":"inherit","linkDebounce":"100","name":"10Gbps_autoNeg_OFF","nameAlias":"","ownerKey":"","ownerTag":"","speed":"10G"}}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)
    
    #=====LLDP Policies=====
    print('\n**********Creating LLDP_OFF policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/lldpIfP-LLDP_OFF.json'    
    payload = '{"lldpIfPol":{"attributes":{"adminRxSt":"disabled","adminTxSt":"disabled","annotation":"","descr":"","dn":"uni/infra/lldpIfP-LLDP_OFF","name":"LLDP_OFF","nameAlias":"","ownerKey":"","ownerTag":""}}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)

    print('\n**********Creating LLDP_ON policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/lldpIfP-LLDP_ON.json'    
    payload = '{"lldpIfPol":{"attributes":{"adminRxSt":"enabled","adminTxSt":"enabled","annotation":"","descr":"","dn":"uni/infra/lldpIfP-LLDP_ON","name":"LLDP_ON","nameAlias":"","ownerKey":"","ownerTag":""}}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)

    #=====PortChannel Policies=====
    print('\n**********Creating PortChannel mode ON policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/lacplagp-PC_mode_ON.json'    
    payload = '{"lacpLagPol":{"attributes":{"dn":"uni/infra/lacplagp-PC_mode_ON","name":"PC_mode_ON","rn":"lacplagp-PC_mode_ON","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)    
    
    print('\n**********Creating PortChannel LACP Active policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/lacplagp-PC_LACP_ACTIVE.json'    
    payload = '{"lacpLagPol":{"attributes":{"dn":"uni/infra/lacplagp-PC_LACP_ACTIVE","name":"PC_LACP_ACTIVE","mode":"active","rn":"lacplagp-PC_LACP_ACTIVE","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)     

    print('\n**********Creating PortChannel LACP Passive policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/lacplagp-PC_LACP_PASSIVE.json'    
    payload = '{"lacpLagPol":{"attributes":{"dn":"uni/infra/lacplagp-PC_LACP_PASSIVE","name":"PC_LACP_PASSIVE","mode":"passive","rn":"lacplagp-PC_LACP_PASSIVE","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)
    
    #=====STP Policies=====
    print('\n**********Creating STP BPDU Filter policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/ifPol-STP_BPDU_FILTER.json'    
    payload = '{"stpIfPol":{"attributes":{"dn":"uni/infra/ifPol-STP_BPDU_FILTER","name":"STP_BPDU_FILTER","ctrl":"bpdu-filter","rn":"ifPol-STP_BPDU_FILTER","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)     
    
    print('\n**********Creating STP BPDU Guard policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/ifPol-STP_BPDU_GUARD.json'    
    payload = '{"stpIfPol":{"attributes":{"dn":"uni/infra/ifPol-STP_BPDU_GUARD","name":"STP_BPDU_GUARD","ctrl":"bpdu-guard","rn":"ifPol-STP_BPDU_GUARD","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response) 
    
    print('\n**********Creating STP BPDU Guard and FILTER policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/ifPol-STP_BPDU_GUARD_and_FILTER.json'    
    payload = '{"stpIfPol":{"attributes":{"dn":"uni/infra/ifPol-STP_BPDU_GUARD_and_FILTER","name":"STP_BPDU_GUARD_and_FILTER","ctrl":"bpdu-filter,bpdu-guard","rn":"ifPol-STP_BPDU_GUARD_and_FILTER","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)    
    
    #=====MCP Policies=====
    print('\n**********Creating MCP ENABLED policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/mcpIfP-MCP_ENABLED.json'    
    payload = '{"mcpIfPol":{"attributes":{"dn":"uni/infra/mcpIfP-MCP_ENABLED","name":"MCP_ENABLED","rn":"mcpIfP-MCP_ENABLED","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)     
    
    print('\n**********Creating MCP DISABLED policy**********')
    url = 'https://'+apic_ip+'/api/node/mo/uni/infra/mcpIfP-MCP_DISABLED.json'    
    payload = '{"mcpIfPol":{"attributes":{"dn":"uni/infra/mcpIfP-MCP_DISABLED","name":"MCP_DISABLED","adminSt":"disabled","rn":"mcpIfP-MCP_DISABLED","status":"created"},"children":[]}}'
    response = session.post(url, verify=False, data=payload, headers=headers)
    check_response(response)    
    
#=======================================================================
def check_response(response):
    if str(response.status_code) == '200':
        print('success...')
    else:
        print(str(response.text))

#=======================================================================
    
def get_tenant_info(file_name):
    os.system('cls||clear')

    print('\n\n\nGetting tenant info from {}'.format(file_name))

    book = xlrd.open_workbook(file_name)
    xl_sheet = book.sheet_by_name('tenants')
    num_rows=xl_sheet.nrows
    tenant_list = []
    for row in range(1, num_rows):
        tenant_info = {}
        tenant_name = str(xl_sheet.cell(row,0).value)
        tenant_desc = str(xl_sheet.cell(row,1).value)
        tenant_info = { 'name' : tenant_name, 'desc' : tenant_desc}
        tenant_list.append(tenant_info)
    print('***** Found these Tenants to configure *****')
    for tenant in tenant_list:
        print('Tenant name: {}\t - description: {}'.format(tenant_info['name'], tenant_info['desc']))
    
    while True:
        answer = raw_input('\nIs the above correct? (y/Y/n/N)').lower()
        if answer == 'y':
            return tenant_list
        elif answer == 'n':
            print('Please fix the spreadsheet with correct data')
            print('Exiting...')
            exit()
        else:
            print("Please enter 'y' or 'Y' or 'n' or 'N'")
            
#=======================================================================


#=======================================================================


#=======================================================================

            
#=============MAIN Start==========================================================

start_msg(apic_ip)

nodes_dict = get_node_info(file_name)
session = login_apic(apic_ip, username, password)
#add_nodes(apic_ip, session, nodes_dict)
#add_intf_pols(apic_ip, session)
tenant_list = get_tenant_info(file_name)

#todo...use tenant_list to create tenant etc...

print('Done...')





