# aci-init
To quickly initialise an ACI fabric with policies etc

The 'initialize_fabric.py' file is the main file and uses the 'fabric_init.xlsx' file to create some of the ACI objects in the fabric.
Basically the xlsx file has a bunch of info regarding the nodes (spines and leafs) and will use this to register and config the Out-of-Band management info.

It also creates another user called 'nexio'

It then also creates a bunch of generic policies that is normally used in the Fabric.
Currently creating:
   CDP_OFF 
   CDP_ON
   1Gbps_autoNeg_ON
   1Gbps_autoNeg_OFF 
   10Gbps_autoNeg_ON 
   10Gbps_autoNeg_OFF 
   LLDP_OFF
   LLDP_ON 
   PortChannel mode ON
   PortChannel LACP Active
   PortChannel LACP Passive
   STP BPDU Filter
   STP BPDU Guard
   STP BPDU Guard and FILTER
   MCP ENABLED
   MCP DISABLED
   
   And then lastly the work in progress part is where we would use the same xlsx sheet to add tenants, VRFs and BD's etc...
   
   The other files are all used to test simple tasks etc...and int he 'aci_json_objects' folder there are some json objects used for ACI stuff ;-)
     
    Have fun.
