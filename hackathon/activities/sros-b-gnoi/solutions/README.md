# Solutions for SR OS gNOI Hackathon Activity

## Confiuration Backups - Solution

The goal of this hackathon activity is to establish regular configuration backups of your SR OS device on an external machine.

Try writing a script in the language of your choice that will use gNOI file service to get the configuration file (cf3:\CONFIG.CFG) from the device. After the file transfer is completed, rename the file with the current timestamp and copy it to a directory specifically created for backups.

Schedule this script to run every 10 minutes on the host VM.

Let's see how this script will look like with shell scripting:

```
#!/bin/bash

## Setting the home directory
# (Replace with your current working dir)
cur_dir=/home/nokia/sros-gnoi

## Running gNOI to get the configuration file
/usr/local/bin/gnoic -a clab-srexperts-p1 --insecure -u admin -p SReXperts2024 file get --file cf3:\CONFIG.CFG --dst $cur_dir/

## Renaming the configuration file with current timestamp and moving it to backups directory
mv $cur_dir/cf3:/CONFIG.CFG $cur_dir/backups/config.cfg.$(date +%F-%H:%M:%S)
```

Now that our script is ready, let's run it once to verify whether it works.

```
# chmod +x backup.sh
# mkdir backups
# ./backup.sh
INFO[0000] "clab-srexperts-p1:57400" file "cf3:\\CONFIG.CFG" saved 

# ls -lrt backups/
total 0
-rw-r--r-- 1 nokia nokia 0 May 15 03:27 config.cfg.2024-05-15-03:27:55

```

Great job ! The script works as expected.

Let's schedule the script to run every 10 minutes on the server.

Use `crontab -e` to edit the crontab and add the below line at the end.

```
0,10,20,30,40,50 * * * * /usr/bin/bash /home/nokia/sros-gnoi/backup.sh>/dev/null 2>&1 (Replace the path with your working directory)
```

Check the `/home/nokia/srl-gnoi/backups` directory to verify that that the backups are being taken periodically.

## Bulk File Transfers - Solution

Your Engineering team has given you the responsibility to create 2 new loopbacks on all 1000 SR OS devices in your network.

The goal of this hackathon activity is to use gNOI file service to transfer files to your SR OS device.

Try writing a script in the language of your choice that will use gNOI file service to run through a list of devices and transfer the configuration file that holds the commands to configure these loopbacks.

Create a file on your local VM with the commands to configure loopbacks on SR OS.

```
/configure router interface <your-name>-gnoi-LB1 loopback ipv4 primary address 192.168.24.10 prefix-length 32
/configure router interface <your-name>-gnoi-LB2 loopback ipv4 primary address 192.168.24.20 prefix-length 32
```

Let's see how this script will look like with shell scripting. In our example, we only have 1 device in the list.

File with loopback commands and node list:

```
# cat loopback.txt
/configure router interface <your-name>-gnoi-LB1 loopback ipv4 primary address 192.168.24.10 prefix-length 32
/configure router interface <your-name>-gnoi-LB2 loopback ipv4 primary address 192.168.24.20 prefix-length 32

# cat node-list.txt
clab-srexperts-p1
```

```
#!/bin/bash

## Setting the home directory
# (Replace with your current working dir)
cur_dir=/home/nokia/sros-gnoi 

## Running through the list of devices
for i in `awk '{print $0}' $cur_dir/node-list.txt`
        do
            ## Initializing the filename variable
            filename=""
            ## Transfer the package to the device
            gnoic -a $i -u admin -p SReXperts2024 --insecure file put --file $cur_dir/loopback.txt --dst cf3:\loopback.txt
            ## List the package on the device
            filename=`gnoic -a $i -u admin -p SReXperts2024 --insecure file stat --path cf3:\loopback.txt --format json | grep path | awk -F'\"' '{print $4}'`
            ## Check if file package exists on the device
			if  [[ -n "$filename" ]];
				then
					echo "File transferred successfully to $i"
				else
					echo "File not transferred to $i. Please try again."
			fi
		done   
```

Now that our script is ready, let's run it

```
# chmod +x file-transfer.sh
# ./file-transfer.sh
INFO[0000] "clab-srexperts-p1:57400" sending file="/home/nokia/sros-gnoi/loopback.txt" hash 
INFO[0000] "clab-srexperts-p1:57400" file "/home/nokia/sros-gnoi/loopback.txt" written successfully 
File transferred successfully to clab-srexperts-p1
```

Verify that the file was transferred to the router.

```
[/]
A:admin@p1# file show cf3:/loopback.txt
File: loopback.txt
-------------------------------------------------------------------------------
/configure router interface <your-name>-gnoi-LB1 loopback ipv4 primary address 192.168.24.10 prefix-length 32
/configure router interface <your-name>-gnoi-LB2 loopback ipv4 primary address 192.168.24.20 prefix-length 32

===============================================================================
```

Note - The same use case also applies to file transfer of software images as part of the software upgrade process.


## Bulk File Deletions - Solution

Let's assume we completed a network wide software upgrade 6 months ago and now we can initiate a deletion of the old software files from our devices in order to reduce the flash disk usage.

The goal of this hackathon activity is to use gNOI file service to verify that the file exists on the device and then delete the old software files on all routers in your network.

Try writing a script in the language of your choice that will use gNOI file service to run through a list of devices, list the file and delete file on each device.

Since we are using containerlab for this hackathon and there are no software files stored on SR OS container nodes deployed in this lab, we will be deleting the configuration file we transferred in the previous use case.

Let's see how this script will look like with shell scripting. In our example, we only have 1 device in the list.

Our file with the list of nodes looks like this:

```
# cat node-list.txt
clab-srexperts-p1
```


```
#!/bin/bash

## Setting the home directory
# (Replace with your current working dir)
cur_dir=/home/nokia/sros-gnoi

## Running through the list of devices
for i in `awk '{print $0}' $cur_dir/node-list.txt`
        do
                ## Initializing the filename variable
				filename=""
				## Delete the file on the device
				gnoic -a $i -u admin -p SReXperts2024 --insecure file remove --path cf3:\loopback.txt
                ## List the file on the device to confirm file is deleted
				filename=`gnoic -a $i -u admin -p SReXperts2024 --insecure file stat --path cf3: --format json | grep loopback.txt | awk -F'\"' '{print $4}'`
                ## Check if filename returned is valid.
				if [[ -z "$filename" ]];
                then
                        echo "File deleted successfully from $i"
                else
                        echo "File $filename not deleted from $i. Please try again !"
                fi
        done
```

Now that our script is ready, let's run it

```
# chmod +x file-delete.sh
# ./file-delete.sh
INFO[0000] "clab-srexperts-p1:57400" file "cf3:loopback.txt" removed successfully 
File deleted successfully from clab-srexperts-p1
```

Verify that the file was deleted on the router.

```
[/]
A:admin@p1# file show cf3:/loopback.txt
MINOR: MGMT_AGENT #2007: Operation failed - open file "cf3:\loopback.txt"
```
