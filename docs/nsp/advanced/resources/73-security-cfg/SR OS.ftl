<#setting number_format="computer">
{
    "[${site.ne\-name}] disable insecure protocols": {
        "config": {
            "target": "nokia-conf:/configure/system/security",
            "operation": "merge",
            "value": {
                "nokia-conf:security": {
                    "telnet-server": false,
                    "telnet6-server": false,
                    "ftp-server": false
                }
            }
        }
    },
    "[${site.ne\-name}] management-access-filter": {
        "config": {
            "target": "nokia-conf:/configure/system/security/management-access-filter",
            "operation": "replace",
            "value": {
                "nokia-conf:management-access-filter": {
                    "ip-filter": {
                        "admin-state": "enable",
                        "default-action": "accept",
                        "entry": [
                            {
                                "entry-id": 10,
                                "description": "Allow CLI\/SFTP over SSH",
                                "action": "accept",
                                "match": {
                                    "mgmt-port": {
                                        "cpm": [null]
                                    },
                                    "dst-port": {
                                        "port": 22
                                    }
                                }
                            },
                            {
                                "entry-id": 20,
                                "description": "Allow NETCONF",
                                "action": "accept",
                                "match": {
                                    "mgmt-port": {
                                        "cpm": [null]
                                    },
                                    "dst-port": {
                                        "port": 830
                                    }
                                }
                            },
                            {
                                "entry-id": 30,
                                "description": "Allow gRPC",
                                "action": "accept",
                                "match": {
                                    "mgmt-port": {
                                        "cpm": [null]
                                    },
                                    "dst-port": {
                                        "port": 57400
                                    }
                                }
                            },
                            {
                                "entry-id": 40,
                                "description": "Allow ICMP",
                                "action": "accept",
                                "match": {
                                    "protocol": "icmp",
                                    "mgmt-port": {
                                        "cpm": [null]
                                    }
                                }
                            },
                            {
                                "entry-id": 50,
                                "description": "Allow SNMP",
                                "action": "accept",
                                "match": {
                                    "protocol": "udp",
                                    "src-port": {
                                        "port": 162
                                    },
                                    "dst-port": {
                                        "port": 162
                                    },
                                    "mgmt-port": {
                                        "cpm": [null]
                                    }
                                }
                            },
                            {
                                "entry-id": 100,
                                "description": "log all other protocols",
                                "action": "accept",
                                "log-events": true,
                                "match": {
                                    "mgmt-port": {
                                        "cpm": [null]
                                    }
                                }
                            }
                        ]
                    },
                    "ipv6-filter": {
                        "default-action": "accept"
                    },
                    "mac-filter": {
                        "default-action": "accept"
                    }
                }
            }
        }
    },
    "[${site.ne\-name}] cpm filter": {
        "config": {
            "target": "nokia-conf:configure/system/security",
            "operation": "merge",
            "value": {
                "nokia-conf:security": {
                    "cpm-filter": {
                        "default-action": "accept",
                        "ip-filter": {
                            "admin-state": "enable",
                            "entry": [
                                {
                                    "entry-id": 10,
                                    "action": {
                                        "accept": [null]
                                    },
                                    "match": {
                                        "protocol": "icmp"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    },
    "[${site.ne\-name}] BGP Best Practices": {
        "config": {
            "target": "nokia-conf:configure/router=Base/bgp/error-handling",
            "operation": "merge",
            "value": {
                "nokia-conf:error-handling": {
                    "update-fault-tolerance": true
                }
            }
        }
    },
    "[${site.ne\-name}] security logs": {
        "config": {
            "target": "nokia-conf:/configure/log/log-id=90",
            "operation": "replace",
            "value": {
                "nokia-conf:log": {
                    "name": "90",
                    "source": {
                        "security": true
                    },
                    "destination": {
                        "memory": {
                            "max-entries": 1000
                        }
                    }
                }
            }
        }
    }
}
