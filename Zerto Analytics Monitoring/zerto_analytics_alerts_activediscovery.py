"""/*******************************************************************************
 * written by Adam Sims 
  Gets all active alerts from Zerto Analytics and pipes them into LogicMonitor. The Datasource should be set to alert if the instance exists. 
 * Example of logging into the API 
 https://www.zerto.com/blog/analytics/unleashing-the-power-of-zerto-analytics-api/

 swagger Documentation
 https://docs.api.zerto.com/#/Monitoring/get_v2_monitoring_sites

 C:\Program Files\Python39\python.exe
 "C:\Program Files (x86)\LogicMonitor\Agent\lib\zerto_analytics_alerts_activediscovery.py" ##zaUser## ##zaPassword##
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
    """Gets each active alert in the zerto analytics portal and displays them as instances in LogicMonitor"""
    #Log into Zerto Analytics
    zerto_analytics_token = za_login()
    #Adds the token to the headers list
    headers['Authorization'] = "Bearer " + zerto_analytics_token
    #get all alerts
    all_alerts = za_session.get('https://analytics.api.zerto.com/v2/monitoring/alerts', headers=headers)
    if all_alerts.ok:
        parsed_alerts = json.loads(all_alerts.content)
        for alert in parsed_alerts:
            #Obtain variables
            #alert Properties
            alert_identifier = alert['identifier']
            alert_type = alert['type']
            alert_severity = alert['severity']
            alert_description = alert['description'].strip()
            alert_entityType = alert['entityType']
            alert_affectedZorgs = alert['affectedZorgs']
            alert_collectionTime = alert['collectionTime']
            alert_collectionTime = alert['collectionTime'].replace("T"," ")
            alert_site = alert['site']
            site_name = alert_site['name']
            site_name = site_name.replace(" ","")
            site_name = site_name.replace("(","")
            site_name = site_name.replace(")","")
            site_name = site_name.replace("'","")
            site_name = site_name.replace(",","")
            site_name = site_name.replace(".","")
            site_type = alert_site['type']
            site_identifier = alert_site['identifier']
            wild_value = alert_type + "-" + alert_identifier

            #print("format for LM: wildVALUE ## WildALIAS ## Description #### auto properties")
            print(f"{wild_value}##{wild_value}##{alert_severity} {alert_description}####auto.alert_identifier={alert_identifier}&auto.alert_type={alert_type}&auto.alert_severity={alert_severity}&auto.alert_entityType={alert_entityType}&auto.alert_affectedZorgs={alert_affectedZorgs}&auto.site_name={site_name}&auto.site_type={site_type}&auto.site_identifier={site_identifier}&auto.alert_collectionTime={alert_collectionTime}\n")
    else:
        errorText = "Response code: " + str(all_vms.status_code) + " Reason: " + all_vms.reason + "Response Text: " + all_vms.text
        raise Exception(errorText)


if __name__ == '__main__':
    za_session = requests.Session()
    main()