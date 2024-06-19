from pyvim import connect
from pyVmomi import vim
import time

#ADVANCED SETTING TO REMOVE VCLS VM's
def set_vcls_advanced(service_instance):
    service_instance = connect.SmartConnect(host=viserver, user=username, pwd=password)

    # GET CLUSTER DOMAIN NUMBER
    content = service_instance.RetrieveContent()
    view_manager = content.viewManager
    container_view = view_manager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True)

    for obj in content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True).view:
        if obj.name == cluster_name:
            cluster = obj
            break

    if cluster is not None:
        cluster_id = cluster._moId
        # GET LAST 14 CHARACTERS OF STRING
        adv_string1 = 'config.vcls.clusters.'
        adv_setting_name = adv_string1 + cluster_id + '.enabled'

        # CREATE ADVANCED SETTING
        option_manager = content.setting
        option_value = vim.option.OptionValue()
        option_value.key = adv_setting_name
        option_value.value = 'False'
        option_manager.UpdateValues([option_value])

        print("Advanced setting created successfully.")

#DISABLE CLUSTER FUNCTIONS
def disable_cluster_functions(service_instance, cluster_name):
    # Retrieve content
    content = service_instance.RetrieveContent()

    # Find the cluster object
    cluster = None
    for cluster_obj in content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True).view:
        if cluster_obj.name == cluster_name:
            cluster = cluster_obj
            break

    if cluster is None:
        print(f"Cluster '{cluster_name}' not found.")
        return

    # Get the cluster configuration
    config_spec = vim.cluster.ConfigSpecEx()

    # Disable DRS
    config_spec.drsConfig = vim.cluster.DrsConfigInfo()
    config_spec.drsConfig.enabled = False

    # Update the cluster configuration
    task = cluster.ReconfigureComputeResource_Task(config_spec, modify=True)
    print(f"Disabling DRS for cluster '{cluster_name}'. This may take a moment...")

    # Wait for the task to complete
    wait_for_task(task)
    print(f"DRS disabled successfully for cluster '{cluster_name}'.")
    
    # Disable HA
    config_spec.dasConfig = vim.cluster.DasConfigInfo()
    config_spec.dasConfig.enabled = False

    # Update the cluster configuration
    task = cluster.ReconfigureComputeResource_Task(config_spec, modify=True)
    print(f"Disabling HA for cluster '{cluster_name}'. This may take a moment...")

    # Wait for the task to complete
    wait_for_task(task)
    print(f"HA disabled successfully for cluster '{cluster_name}'.")

    # Disable vSAN
    config_spec.vsanConfig = vim.VsanClusterConfigInfo()
    config_spec.vsanConfig.enabled = False

    # Update the cluster configuration
    task = cluster.ReconfigureComputeResource_Task(config_spec, modify=True)
    print(f"Disabling vSAN for cluster '{cluster_name}'. This may take a moment...")

    # Wait for the task to complete
    wait_for_task(task)
    print(f"vSAN disabled successfully for cluster '{cluster_name}'.")

def wait_for_task(task):
    """Waits and monitors a vSphere task to completion."""
    while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
        continue
    if task.info.state == vim.TaskInfo.State.success:
        return True
    elif task.info.state == vim.TaskInfo.State.error:
        print("Task failed: %s" % task.info.error)
        return False

#GET HOST NAMES IN CLUSTER FOR MAINTENANCE MODE
def get_host_names_in_cluster(service_instance, cluster_name):
    # Retrieve content
    content = service_instance.RetrieveContent()

    # Find the cluster object
    cluster = None
    for cluster_obj in content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True).view:
        if cluster_obj.name == cluster_name:
            cluster = cluster_obj
            break

    if cluster is None:
        print(f"Cluster '{cluster_name}' not found.")
        return []

    # Get the host names in the cluster
    host_names = []
    for host in cluster.host:
        host_names.append(host.name)

    return host_names

#PUT HOSTS INTO MAINTENANCE MODE
def host_decom(service_instance, host_names):
    # Retrieve content
    content = service_instance.RetrieveContent()

    # Find the host objects
    host_objects = []
    for host_name in host_names:
        view_ref = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        for host_obj in view_ref.view:
            if host_obj.name == host_name:
                host_objects.append(host_obj)
                break

    if not host_objects:
        print(f"No hosts found with the specified names: {host_names}")
        return

    # Put each host into maintenance mode
    for host_obj in host_objects:
        task = host_obj.EnterMaintenanceMode_Task(timeout=0, evacuatePoweredOffVms=True)
        print(f"Putting host '{host_obj.name}' into maintenance mode. This may take a moment...")

        # Wait for the task to complete
        wait_for_task(task)
        print(f"Host '{host_obj.name}' is now in maintenance mode.")
        
     # Disconnect the host from vCenter
    
    for host_obj in host_objects:
        task = host_obj.Disconnect()
        print(f"Disconnecting hosts from vCenter. This may take a moment...")

    # Wait for the task to complete
    wait_for_task(task)
    print(f"Hosts are disconnected from vCenter.")
    
    # Remove the host from vCenter
    for host_obj in host_objects:
        task = host_obj.Destroy_Task()
        print(f"Removing hosts from vCenter Inventory. This may take a moment...")

    # Wait for the task to complete
    wait_for_task(task)
    print(f"Hosts are removed from vCenter.")
    
def wait_for_task(task):
    """Waits and monitors a vSphere task to completion."""
    while task.info.state in [vim.TaskInfo.State.running, vim.TaskInfo.State.queued]:
        continue
    if task.info.state == vim.TaskInfo.State.success:
        return True
    elif task.info.state == vim.TaskInfo.State.error:
        print("Task failed: %s" % task.info.error)
        return False

# Set vCenter credentials
viserver = "<vCenter FQDN>"
username = "administrator@vsphere.local"
password = "VMware1!"

# Connect to vCenter
service_instance = connect.SmartConnect(host=viserver, user=username, pwd=password)

# Cluster name
cluster_name = "Cluster01"
#Host names
host_names = get_host_names_in_cluster(service_instance, cluster_name)

#1) ADD ADVANCED SETTING TO REMOVE VCLS VM'S FROM CLUSTER
set_vcls_advanced(service_instance)
time.sleep(5)

#2) DISABLE HA, DRS & VSAN ON CLUSTER
disable_cluster_functions(service_instance, cluster_name)
time.sleep(5)

#3) PUT HOSTS INTO MAINTENANCE MODE, DISCONNECT AND REMOVE FROM VCENTER
host_decom(service_instance, host_names)
time.sleep(5)

# Disconnect from vCenter
connect.Disconnect(service_instance)
