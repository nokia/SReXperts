<#setting number_format="computer">
<#assign sessionname="${site['ne-name']}_to_${site.peer['ne-name']}_${target}">

{
    "TWAMP REFLECTOR": {
      "config": {
        "target": "nokia-conf:/configure/router=Base/twamp-light/reflector",
        "operation": "merge",
        "value": {
          "nokia-conf:reflector": {
              "admin-state": "enable",
              "udp-port": 64364,
              "type": "twamp-light",
              "prefix": [
                {
                    "ip-prefix": "::\/0",
                    "description": "all ipv6"
                },
                {
                    "ip-prefix": "0.0.0.0\/0",
                    "description": "all ipv4"
                }
              ]
          }
        }
      }
    },

    "TWAMP STREAMING TEMPLATE": {
      "config": {
        "target": "nokia-conf:/configure/oam-pm/streaming",
        "operation": "merge",
        "value": {
          "nokia-conf:streaming": {
              "delay-template": [
                  {
                      "delay-template-name": "common",
                      "admin-state": "enable",
                      "sample-window": 10,
                      "window-integrity": 90,
                      "fd-avg": [
                          {
                              "direction": "round-trip"
                          }
                      ],
                      "ifdv-avg": [
                          {
                              "direction": "round-trip"
                          }
                      ]
                  }
              ]
          }
        }
      }
    },

    "PM ACCOUNTING POLICY": {
      "config": {
        "target": "nokia-conf:/configure/log/accounting-policy=75",
        "operation": "merge",
        "value": {
          "nokia-conf:accounting-policy": {
            "policy-id": 75,
            "admin-state": "enable",
            "include-system-info": true,
            "record": "complete-pm",
            "destination": {
                "file": "75"
            }
          }
        }
      }
    },

    "PM ACC FILE POLICY": {
      "config": {
        "target": "nokia-conf:/configure/log/file=75",
        "operation": "merge",
        "value": {
          "nokia-conf:file": {
            "file-policy-name": "75",
            "rollover": 5,
            "retention": 4,
            "compact-flash-location": {
                "primary": "cf3"
            }
          }
        }
      }
    },

    "TWAMP SESSION ${target}": {
      "config": {
        "target": "nokia-conf:/configure/oam-pm/session=${sessionname}",
        "operation": "replace",
        "value": {
          "nokia-conf:session": {
            "session-name": "${sessionname}",
            "session-type": "proactive",
            "ip": {
                "destination": "${site.peer['ne-id']}",
                "destination-udp-port": 64364,
                "router-instance": "Base",
                "source": "${site['ne-id']}",
                "twamp-light": {
                    "admin-state": "enable",
                    "test-id": "${target}",
                    "interval": 100,
                    "record-stats": "delay-and-loss",
                    "delay-template": "common"                                       
                }
            },
            "measurement-interval": [{
                "duration": "5-mins",
                "clock-offset": 0,
                "intervals-stored": 1,
                "accounting-policy": 75
            }]
          }
        }
      }
    }
}