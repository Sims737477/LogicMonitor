These DataSources work together to provide monitoring for your Zerto Solution.

DataSources included in package: 
zerto_analytics_protectedvms_activediscovery.py
zerto_analytics_dataretrieval_batchscript.py
zerto_analytics_alerts_activediscovery.py

To implement these DataSources, add "analytics.api.zerto.com" as a device in LogicMonitor. Add the properties zaPassword and zaUser to the resource. These should be your zerto analytics account. We had a service account created specifically for this. Then create 2 DataSources, one for Protected VM's and another for Alerts using the "Upload script file" functionality.  


DataSource Functionality:

    Protected VM's:

        zerto_analytics_protectedvms_activediscovery.py:Should be used as the Active Discovery script. Will get all protected VM's and list them by zorg. Includes the following Auto properties: 
            auto.vmidentifier	
            auto.vmname	
            auto.vmprovisionedstorage
            auto.vpgconfiguredrpo
            auto.vpgidentifier
            auto.vpgname	
            auto.zorgname	


        zerto_analytics_dataretrieval_batchscript.py: Should be used as the Collector Attributes script, paired with the script above. This will collect the following Normal data points: 
            ProvisionedStorageInMB
            UsedStorage
            VMState
            VMStatus
            vpgActualRPO

            Recommended Complex DataPoints: 
            ActualRPOMinutes
            RPOinHours
            StorageInGB

    Zerto Analytics Alerts:

        zerto_analytics_alerts_activediscovery.py: Using this Datasource effectively turns LogicMonitor into a Proxy for Zerto Analytics alerts. This script should be set as the Active Discovery Script.The Collector Attributes should be left blank. Then Each active alert will appear in the portal, the alert themselves are built to read 1:1 from the analytics portal. If no active alerts, no instances are found and the DataSource will not appear under the resource. Use filtering in the LM DataSource to exclude unecessary alerts. Normal Datapoints: Alert Trigger, should be a gauge, the raw Metric should be exitCode, and the alert threshold should be set to 0, repeating for different thresholds. This will trigger the alert if any exist. 



