<#setting number_format="computer">
{
    "[${site.ne\-name}] explicitly disable FTP": {
        "config": {
            "target": "srl_nokia-system:/system/srl_nokia-ftp:ftp-server",
            "operation": "replace",
            "value": {
                "srl_nokia-ftp:ftp-server": {
                    "network-instance": [
                        {
                            "name": "mgmt",
                            "source-address": "::",
                            "timeout": 300,
                            "session-limit": 20,
                            "admin-state": "disable"
                        },{
                            "name": "default",
                            "source-address": "::",
                            "timeout": 300,
                            "session-limit": 20,
                            "admin-state": "disable"
                        }
                    ]
                }
            }
        }
    },
    "[${site.ne\-name}] Rate limit the SSH server": {
        "config": {
            "target": "srl_nokia-system:/system/srl_nokia-ssh:ssh-server",
            "operation": "merge",
            "value": {
                "srl_nokia-ssh:ssh-server": {
                    "name": "mgmt",
                    "rate-limit": 10
                }
            }
        }
    },
    "[${site.ne\-name}] Append entries to the CPM filter": {
        "config": {
            "target": "srl_nokia-acl:/acl",
            "operation": "merge",
            "value": {
                "srl_nokia-acl:acl": {
                    "acl-filter": [
                        {
                            "name": "cpm",
                            "type": "ipv4",
                            "entry": [
                                {
                                    "sequence-id": 1050,
                                    "match": {
                                        "ipv4": {
                                            "protocol": "tcp"
                                        },
                                        "transport": {
                                            "destination-port": {
                                                "value": 2200
                                            }
                                        }
                                    }
                                }
                            ]
                        },
                        {
                            "name": "cpm",
                            "type": "ipv6",
                            "entry": [
                                {
                                    "sequence-id": 1050,
                                    "match": {
                                        "ipv6": {
                                            "next-header": 6
                                        },
                                        "transport": {
                                            "destination-port": {
                                                "value": 2200
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
}