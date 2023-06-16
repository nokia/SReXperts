# SROS gNOI Certificates Management

The goal of this lab is to add a certificate profile to an SROS router and manage the certificates lifecycle using gNOI (gRPC Network Operations Interface).

**Grading: intermediate**

## Deploying the lab

```shell
sudo containerlab deploy -c -t certs.clab.yml
```

## Tools needed  

| Role | Software |
| --- | --- |
| Lab Emulation | [containerlab](https://containerlab.dev/) |
| Configuration and telemetry tool | [gNMIc](https://gnmic.openconfig.net/) |
| Certificate generation and lifecycle      | [gNOIc](https://gnoic.kmrd.dev)   |

## Tasks

* **Enable gNOI**

Enable gNOI Cert-mgmt

XPATH: `/configure/system/grpc/gnoi/cert-mgmt`
CLI:   `configure system grpc gnoi cert-mgmt`

Authorize gNOI cert-mgmt RPCs

XPATH: `/configure/system/security/aaa/local-profiles/profile[user-profile-name="administrative"]/grpc/rpc-authorization`
CLI:   `configure system security aaa local-profiles profile administrative grpc rpc-authorization`

* **Generate a self signed CA certificate keypair**

Generate a self signed certificate keypair using gNOIc

gNOIc cmd: [cert create-ca](`https://gnoic.kmrd.dev/command_reference/cert/create-ca/)

* **Install a new certificate**

Install a new certificate

gNOIc cmd: [cert install](https://gnoic.kmrd.dev/command_reference/cert/install/)

Check the certificate

gNOIc cmd: [cert get](https://gnoic.kmrd.dev/command_reference/cert/get/)

* **Create a Certificate Profile**

XPATH:  `/configure/system/security/tls/cert-profile`
CLI:    `configure system security tls cert-profile`

* **Create Cipher lists**

XPATH:  `/configure/system/security/tls/server-cipher-list/tls12-cipher`
        `/configure/system/security/tls/server-cipher-list/tls13-cipher`
CLI:    `configure system security tls server-cipher-list`

* **Create server-tls-profile**

XPATH:  `/configure/system/security/tls/server-tls-profile`
CLI:    `configure system security tls server-tls-profile`

* **Change the gRPC server from unsecure to secure**

XPATH:  `/configure/system/grpc`
CLI:    `configure system grpc`

* **Validate that the gRPC server accepts secure connections**

* **Rotate the certificate**

Rotate the certificate while there is an ongoing gNMI session.

gNOIc cmd: [cert rotate](https://gnoic.kmrd.dev/command_reference/cert/rotate/)

* **Revoke the certificate**

Revoke the certificate while there is an ongoing gNMI session.

gNOIc cmd: [cert revoke](https://gnoic.kmrd.dev/command_reference/cert/revoke/)
