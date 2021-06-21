"""/*******************************************************************************
 * written by Adam Sims 
 Retrieves Protected VM data. Pairs with zerto_analytics_protectedvms_activediscovery.py
 
 * Example of logging into the API 
 https://www.zerto.com/blog/analytics/unleashing-the-power-of-zerto-analytics-api/

 swagger Documentation
 https://docs.api.zerto.com/#/Monitoring/get_v2_monitoring_sites

 C:\Program Files\Python39\python.exe
 "C:\Program Files (x86)\LogicMonitor\Agent\lib\zerto_analytics_dataretrieval_batchscript.py" ##zaUser## ##zaPassword##
 ******************************************************************************/"""
import sys
import requests
import json
import hashlib
import base64
import time
import hmac
from requests.auth import HTTPBasicAuth

##Global Variables##
#Username and password for Zerto Analytics along with the original headers for authentication. The Token is added after. 
ZA_USERNAME = str(sys.argv[1])
ZA_PASSWORD = str(sys.argv[2])
headers = {'Accept': 'application/json','Content-Type': 'application/json'}

#username and password json object construction to pass to zerto for token request.
data = '{"username": "' + ZA_USERNAME + '","password":"' + ZA_PASSWORD + '"}'

#Base URL 
url = 'https://analytics.api.zerto.com/v2/auth/token' 

#Possible states of a VM 
VM_STATES = {'None':0,'InitialSync':1,'Creating':2,'VolumeInitialSync':3,'Sync':4,'RecoveryPossible':5,'DeltaSync':6,'NeedsConfiguration':7,'FullSync':8,'VolumeDeltaSync':9,'VolumeFullSync':10,
'Promoting':11,'MovingCommitting':12,'MovingBeforeCommit':13,'MovingRollingBack':14,'Deleting':15,'PendingRemove':16,'BitmapSync':17,'ReplicationPausedUserInitiated':18,'Backup':19,'RollingBack':20,
'AddedVmsInInitialSync':21,'Error':22,'EmptyProtectionGroup':23,'DisconnectedFromPeerNoRecoveryPoints':24,'FailingOverCommitting':25,'FailingOverBeforeCommit':26,'FailingOverRollingBack':27,'DisconnectedFromPeer':28,
'ReplicationPausedSystemInitiated':29,'RecoveryStorageProfileError':30,'RecoveryStorageError':31,'JournalStorageError':32,'VmNotProtectedError':33,'JournalOrRecoveryMissingError':34,
'ReplicationPausedForMissingVolume':35
}

#Possible VM Statuses
VM_STATUSES = {'Initializing':0, 'MeetingSLA':1, 'NotMeetingSLA':2, 'RpoNotMeetingSLA':3, 'HistoryNotMeetingSLA':4, 'FailingOver':5, 'Moving':6, 'Deleting':7,
        'Recovered':8, 'Inactive':9}

###Functions###

#Function that returns the API Token needed to pull statistics 
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

def main():
    """Gets each Protected VM/VPG/Zorg data and prints it out in key value pairs format for LM"""
    #Calls the login function that returns the analytics api token needed to make additional requests. Then adds the token to the headers for future requests Might make more sense to have 
    zerto_analytics_token = za_login()

    #Adds the token to the headers list
    headers['Authorization'] = "Bearer " + zerto_analytics_token

    all_vms = za_session.get('https://analytics.api.zerto.com/v2/monitoring/protected-vms', headers=headers)
    
    if all_vms.ok:
        #converts JSON data to Python object
        parsed_vms = json.loads(all_vms.content)
        for vm in parsed_vms:
            #Obtain variables
            #VM Properties
            vm_name = vm['name'] 
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

            #VPG Data (Stuff that changes)
            #checks static dictionary above and returns status code returns 40 otherwsie
            vm_status = VM_STATUSES.get(vm_vpg_info[0]['status'], 40)
            #checks static dictionary above and returns state code returns 40 otherwsie for testing/alerting
            
            vpg_state = VM_STATES.get(vm_vpg_info[0]['state'], 40)
            vpg_actual_rpo = str(vm_vpg_info[0]['actualRpo'])

            #print("format for LM: wildvalue.VariabletoMonitorname=Data")
            print(f"{vm_name}.VMStatus={vm_status}")
            print(f"{vm_name}.vpgActualRPO={vpg_actual_rpo}")
            print(f"{vm_name}.VMState={vpg_state}")
            print(f"{vm_name}.usedStorageInMB={vm_used_storage}")
            print(f"{vm_name}.ProvisionedStorageInMB={vm_provisioned_storage}\n")
    else:
        errorText = "Response code: " + str(all_vms.status_code) + " Reason: " + all_vms.reason + "Response Text: " + all_vms.text
        raise Exception(errorText)

if __name__ == '__main__':
    za_session = requests.Session()
    main()