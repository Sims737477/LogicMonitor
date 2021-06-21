"""/*******************************************************************************
written by Adam Sims 
Gets all Protected VM's and relevant information from the Zerto Analytics Portal. Prints them out in an LM friendly format.

Example of logging into the API 
 https://www.zerto.com/blog/analytics/unleashing-the-power-of-zerto-analytics-api/

 Swagger Documentation
 https://docs.api.zerto.com/#/Monitoring/get_v2_monitoring_sites

DataSource External Script set up
C:\Program Files\Python39\python.exe
"C:\Program Files (x86)\LogicMonitor\Agent\lib\zerto_analytics_protectedvms_activediscovery.py" ##zaUser## ##zaPassword##
 ******************************************************************************/"""
import sys
import requests
import json
import hashlib
import base64
import time
import hmac
from requests.auth import HTTPBasicAuth
import datetime

#Username and password for Zerto Analytics along with the original headers for authentication. The Token is added later.
ZA_USERNAME = str(sys.argv[1])
ZA_PASSWORD = str(sys.argv[2])
headers = {'Accept':'application/json','Content-Type':'application/json'}

#username and password json object construction to pass to zerto for token request.
data = '{"username": "' + ZA_USERNAME + '","password":"' + ZA_PASSWORD + '"}'

#Base URL 
url = 'https://analytics.api.zerto.com/v2/auth/token' 

###Functions###

def za_login():
    """Returns the String API Token needed to pull statistics
    Returns:
        string: api token used for authentication
    
    Raises:
        ExceptionError: ExceptionError when invalid response is received. 
    """
    response = za_session.post(url, headers=headers, data=data)
    if response.ok:
        response_dictionary = json.loads(response.content)
        token = response_dictionary["token"]
        return token
    else:
        errorText = "Response code: " + str(response.status_code) + " Reason: " + response.reason + "Response Text: " + response.text
        raise Exception(errorText)

def get_zorg(vpg_identifier):
    """Accepts VPG Identifier then returns a String Zorg Name Associated with the VPG

    Args: 
        vpg_identifier (str): Unique VPG Idenitifier returned when getting VPG's

    Returns:
        Sring: Name of Zorg associated with VPG

    Raises:
        ExceptionError: ExceptionError when an invalid response is returned.
    """
    url = 'https://analytics.api.zerto.com/v2/monitoring/vpgs/' + str(vpg_identifier)
    response = za_session.get(url , headers=headers)
    if response.ok:
        parsed = json.loads(response.content)
        summary = parsed['summary']
        return str(summary['zorgName'])
    else:
        errorText = "Response code: " + str(response.status_code) + " Reason: " + response.reason + "Response Text: " + response.text
        raise Exception(errorText)

def main():
    """Gets each Protected VM/VPG/Zorg info and prints it out in instance format for LM"""
    #Call the za_login function that returns the analytics api token needed to make additional requests. Then adds the token to the headers for future requests.
    zerto_analytics_token = za_login()
    #Adds the token to the headers list
    headers['Authorization'] = "Bearer " + zerto_analytics_token

    #print("Now we are going to get all of the VM's in our Zerto Portal. 
    all_vms = za_session.get('https://analytics.api.zerto.com/v2/monitoring/protected-vms', headers=headers)
    if all_vms.ok:
        parsed_vms = json.loads(all_vms.content)
        for vm in parsed_vms:
            #Obtain variables
            #VM Properties
            vm_name = vm['name'] 
            #Strips VM Name so LM can handle the output
            vm_name = vm_name.replace(" ","-")
            vm_name = vm_name.replace("(","")
            vm_name = vm_name.replace(")","")
            vm_name = vm_name.replace("'","")
            vm_name = vm_name.replace(",","")
            vm_name = vm_name.replace(".","")
            vm_identifier = vm['identifier']
            vm_provisioned_storage = str(vm['provisionedStorageMb'])
            
            #VM Data (Stuff that changes)
            vm_used_storage = str(vm['usedStorageMb'])

            #VPG Properties
            vm_vpg_info = vm['vpgs']
            vpg_name = vm_vpg_info[0]['name']
            vpg_configured_rpo = str(vm_vpg_info[0]['configuredRpo'])
            vpg_identifier = vm_vpg_info[0]['identifier']
            vpg_zorg_name = get_zorg(vpg_identifier)

            #VPG Data (Stuff that changes)
            vm_status = vm_vpg_info[0]['status']
            vpg_actual_rpo = str(vm_vpg_info[0]['actualRpo'])   
            vpg_state = vm_vpg_info[0]['state']
            
            #print("format for LM: wildVALUE ## WildALIAS ## Description #### auto properties")
            print(f"{vm_name}##{vm_name}##{vpg_name}####auto.zorgName={vpg_zorg_name}&auto.vmName={vm_name}&auto.vmIdentifier={vm_identifier}&auto.vmProvisionedStorage={vm_provisioned_storage}&auto.vpgName={vpg_name}&auto.vpgConfiguredRPG={vpg_configured_rpo}&auto.vpgIdentifier={vpg_identifier}")
    else: 
        errorText = "Response code: " + str(all_vms.status_code) + " Reason: " + all_vms.reason + "Response Text: " + all_vms.text
        raise Exception(errorText)

if __name__ == '__main__':
    za_session = requests.Session()
    main()

