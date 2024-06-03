# Getting Started with Python for SR OS Using pySROS

The pySROS libraries provide a model-driven management interface for Python developers to integrate with Nokia SR OS.
The libraries provide an API for developers to create applications that can interact with Nokia SR OS devices, whether those applications are executed from a development machine or directly on the router.

**Grading: Beginner**

**Elements: SR OS, pySROS**

## Accessing a lab node

In this lab you will interact with the model-driven SR OS router `PE4`. To access it, use:

```
ssh -l admin clab-srexperts-pe4
```

## High level tasks to complete this project

1. **Make a connection**

    Make a connection to get access to the model-driven interfaces of SR OS. Documentation assistance can be found in the [connection and data handling section here](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.management).


   
2. **Obtain Some Data**

    Having made a connection to an SR OS device, it is important to understand the data structures returned by the `pysros.management.Datastore.get()` function. Data is obtained via the pySROS libraries using the JSON instance-path format which is a format combining the JSON language and the YANG instance identifier. This path can be obtained to any location in SR OS by issuing the `pwc json-instance-path` command.

    * Here is an example of obtaining **state data**, for acquiring `system` interface statistics:

   
         ```
         [/state router "Base" interface "system" statistics]
         A:admin@pe4# pwc json-instance-path
         Present Working Context:
         /nokia-state:state/router[router-name="Base"]/interface[interface-name="system"]/statistics
         ```

      This _Present Working Context_ can be fed to the `get()` method to return requested data:
  
         ```
         data = connection_object.running.get(
             '/nokia-state:state/router[router-name="Base"]/interface[interface-name="system"]/statistics'
          )
         print(data)
         ```

         <details>
         <summary>Result</summary>

      ```
      {'ip': Container({'out-packets': Leaf(0), 'out-octets': Leaf(0), 'out-discard-packets': Leaf(0), 'out-discard-octets': Leaf(0), 'in-packets': Leaf(0), 'in-octets': Leaf(0), 'urpf-check-fail-packets': Leaf(0), 'urpf-check-fail-octets': Leaf(0)}), 'mpls': Container({'out-packets': Leaf(0), 'out-octets': Leaf(0), 'in-packets': Leaf(0), 'in-octets': Leaf(0)})}
      ```
         </details>
    
    * The same procedure can be followed to obtain **configuration data**, Consider a use-case where you required the `system` interface configuration information:

   
        ```
        [gl:/configure router "Base" interface "system"]
        A:admin@pe4# pwc json-instance-path
        Present Working Context:
          /nokia-conf:configure/router[router-name="Base"]/interface[interface-name="system"]
        ```

      This output can be used as the path for `get()` method to return requested information:
  
        ```
        data = connection_object.running.get(
            '/nokia-conf:configure/router[router-name="Base"]/interface[interface-name="system"]'
        )
        print(data)
        ``` 

         <details>
         <summary>Result</summary>

      ```
      {'interface-name': Leaf('system'), 'ipv4': Container({'primary': Container({'address': Leaf('10.46.10.24'), 'prefix-length': Leaf(32)})}), 'ipv6': Container({'address': {'fd00:fde8::10:24': Container({'ipv6-address': Leaf('fd00:fde8::10:24'), 'prefix-length': Leaf(128)})}})}
      ```
         </details>


3. **Configure SR OS Routers**

    It is essential to understand the data structures that can be sent to a router using `pysros.management.Datastore.set()` method. This method can be used for configuration of SR OS devices, and it takes two inputs:

    1. A JSON instance path

    2. The payload in the pySROS data structure format

## Reference documentation

* [Python 3 for the Nokia SR OS (pySROS)](https://network.developer.nokia.com/static/sr/learn/pysros/latest/#python-3-for-the-nokia-service-router-operating-system-pysros)
* [SR OS documentation](https://documentation.nokia.com/sr/)



## Task 1: Getting Connected 
A connection to the device is essential for executing pySROS scripts either locally or remotely. Obtaining a `Connection` object *requires* a few things if you are executing off-box:

  - Hostname
  - Username
  - Password

   ```
   from pysros.management import connect
   def get_connection():
       connection_object = connect(host='hostname', 
                               username='username', 
                               password='password', 
                               port='port', # Optional
                               hostkey_verify=False # Lab only
                           )
	   return connection_object

   connection_object = get_connection()
   ```

When obtaining a `Connection` object directly on the device, the parameters are not required, if they are provided, they are simply ignored. This `Connection` object is what will be used to communicate with the routers model-driven API.


## Task 2: Obtain data from running/candidate and state using `get()` function

Create a simple Python script using the pySROS libraries to obtain some data and print it to the screen. This may be done on the device itself using the file edit command, or in `/home/nokia/clab-srexperts/pe4/tftpboot/get.py` that can be run locally on the router via `pyexec tftp://172.31.255.29/get.py` command, either on your local machine or the lab server.

To test your code remotely ensure your Connection object has all the required parameters and just run it. Communication with the node will be handled by pySROS.

Extension: use filters to select the items which their values are desired. Examples can be found in [Example using filters](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros-management-datastore-get-example-content-node-filters).



- ### Exercise: `get()`

    * Obtain dhcpv4 pool configuration data in `vprn "bng-vprn" dhcp-server`


    <details>
    <summary>Example solution</summary>

    ```
    
    from pysros.management import connect

    def main():
    
        connection_object = connect(
            host="host name",
            username="username",
            password="password",
            hostkey_verify=False,
        )
        data = connection_object.running.get(
            '/nokia-conf:configure/service/vprn[service-name="bng-vprn"]/dhcp-server/dhcpv4',
            filter={
                "pool": {},
            },
        )
        print(data)
        print("\n")

    if __name__ == "__main__":
        main()
    ```
    </details>

An example pySROS application for obtaining data is shown in [get.py](./example_solution/get.py) script to get you started.

## Task 3: Configure the router using the `set()` method

Create a simple Python script in `/home/nokia/clab-srexperts/pe4/tftpboot/set.py` that can be run locally on the router via `pyexec tftp://172.31.255.29/set.py` command, to configure a VPRN service by providing path and payload.

The `set()` method takes a number of inputs.  See the documentation [here](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html?highlight=set#pysros.management.Datastore.set).

* **Path** is a json-instance-identifier that can be obtained from a SR OS device using the `pwc json-instance-path` MD-CLI command. The path may point to a YANG `Container`, `List`, `Leaf`, `Leaf-List` or a specific List entry.

    ```
    path = "/nokia-conf:configure/service"
    ```
       
* **Payload** is the value (pySROS data structure) providing the input data for the set() function.

     ```
     payload = {
        "vprn": {
                "service-name": "SERVICE-NAME",
                "admin-state": "enable",
                "service-id": SERVICE-ID,
                "customer": "1",
                "interface": {
                        "interface-name": "INTERFACE-NAME",
                        "admin-state": "enable",
                        "ipv4": {
                            "primary": {
                                "address": "IP ADDRESS",
                                "prefix-length": PREFIX-LENGTH,
                            }
                        },
                        "sap": {"sap-id": "PORT:SERVICE-ID"},
                },
        }
    }
    ```

  and finally the path and payload will be the input for `set()` function for changing or adding a configuration:
      
    ```
    connection_object.candidate.set(path, payload)
    ```

  An example pySROS application for setting configuration can be found [set.py](./example_solution/set.py) script.

  Extension: Data needed for configuring a basic VPRN service could be stored in a YAML file as in the example [vprn.yml](./example_solution/vprn.yml). This example file can be imported and used in the `set()` method as in this example:  [setyaml.py](./example_solution/setyaml.py).

- ### Exercise: `set()`

    * Configure a new subnet (address-range) for the dhcpv4 pool in `vprn "bng-vprn" dhcp-server`


    <details>
    <summary>Solution</summary>

    ```
   
    from pysros.management import connect
    
    
    def main():
    
        connection_object = connect(
            host="host name",
            username="",
            password="",
            hostkey_verify=False,
        )
    
        subnet_path = '/nokia-conf:configure/service/vprn[service-name="bng-vprn"]/dhcp-server/dhcpv4[name="LocalDHCP1"]/pool[pool-name="LocalPool1"]'
        subnet_payload = {
            "subnet": {
                "ipv4-prefix": "10.24.3.0/24",
                "address-range": {
                    "start": "10.24.3.10",
                    "end": "10.24.3.254",
                },
            },
        }
        connection_object.candidate.set(subnet_path, subnet_payload)
        
    if __name__ == "__main__":
        main()
    ```
    </details>
  
## Summary
This use case has given you a working introduction to essential pySROS libraries and functions to manage and interact with Nokia SR OS devices by demonstrating how to establish a connection, retrieve data, and set configurations.
