# pySROS example to provision BGP peering and policies

This Python script uses [pySROS](https://github.com/nokia/pysros) to provision BGP peers and prefix lists based on PeeringDB and IRR data.

## Run example
(assumes you have the lab topology up and running)
```
IXP="AMS-IX" AS2=5678 make
```

This creates a virtual environment, installs the dependencies and launches the sample script
