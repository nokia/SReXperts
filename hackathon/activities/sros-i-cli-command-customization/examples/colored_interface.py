# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.management import connect
from pysros.exceptions import SrosMgmtError
from pysros.pprint import Table

# begin section requiring completion #
RED = ""
MAGENTA = ""
YELLOW = ""
WHITE = ""
GREEN = ""
RESET_COLOR = ""


def color(color, text):
    return "" + text + ""
# end section requiring completion #

def colorState(text):
    if "Up" in text:
        return color(GREEN, text)
    return color(RED,text)


def print_table(rows):
    cols = [
        (32, "Interface-Name\n   IP-Address"),
        (9, "Adm"),
        (11, "Opr(v4/v6)"),
        (7, "Mode"),
        (20, "Port/SapID\nPfxState"),
    ]
    table = Table("",cols, width=79)
    table.printHeader("Interface Table (Router: Base)")
    print("Interface-Name                   Adm       Opr(v4/v6)  Mode    Port/SapId")
    print("   IP-Address                                                  PfxState")
    table.printSingleLine()
    for row in rows:
        print(row)
    table.printSummary(customSummary="Interfaces: " + str(len(rows)))
    table.printFooter()


class RouterInterface():
    def __init__(self, _name, _prefixes, _adm_state, _oper_v4_state, _oper_v6_state, _port_or_sap_id, _mode, _router_name):
        self.name = _name
        self.prefixes = _prefixes
        self.adm_state = "Up" if _adm_state == "enable" else "Down"
        self.oper_v4_state = "Up" if _oper_v4_state == "up" else "Down"
        self.oper_v6_state = "Up" if _oper_v6_state == "up" else "Down"
        self.port_or_sap_id = _port_or_sap_id
        self.mode = "Network" if _mode == "network" else "?"
        self.router_name = _router_name
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        # add 11 to the expected width for color
        RED_width_mod = 0 if not RED  else 11
        MAGENTA_width_mod = 0 if not MAGENTA else 11
        YELLOW_width_mod = 0 if not YELLOW else 11
        WHITE_width_mod = 0 if not WHITE else 11
        GREEN_width_mod = 0 if not GREEN else 11
        RESET_COLOR_width_mod = 0 if not RESET_COLOR else 11
        result = "%-*s%-*s%-*s%-*s%-*s"\
            % (
                33 + MAGENTA_width_mod,
                color(MAGENTA, self.name),
                10 + GREEN_width_mod,
                colorState(self.adm_state),
                12 + GREEN_width_mod + GREEN_width_mod,
                colorState(self.oper_v4_state)+"/"+colorState(self.oper_v6_state),
                8, #8
                self.mode,
                20, #20
                color(MAGENTA, self.port_or_sap_id)
            )
        for prefix in self.prefixes:
            result += "\n   %-*s%-*s" % ( 60 + YELLOW_width_mod, color(YELLOW,prefix[0]), 20, prefix[1]) #60
        return result


def getRouterInterfaces(conn, router_instance="Base"):
    result = []
    x = conn.running.get('/state/router[router-name="'+router_instance+'"]/interface')
    for interface_name, interface_info in x.items():
        try:
            ipv6_address = list(interface_info['ipv6']['address'].values())[0]
            path = '/configure/router[router-name="'+router_instance+'"]/interface[interface-name="' + interface_name + '"]/ipv6/address[ipv6-address="'+ ipv6_address['oper-address'].data +'"]/prefix-length'
            ipv6_pfxlen = str(conn.running.get(path))
            #['prefix-length'].data)

            ipv4_address = interface_info['ipv4']['primary']
            path = '/configure/router[router-name="'+router_instance+'"]/interface[interface-name="' + interface_name + '"]/ipv4/primary'
            ipv4_pfxlen = str(conn.running.get(path, filter={"address":ipv4_address['oper-address'].data})['prefix-length'].data)

            ipv6_ll_address = interface_info['ipv6']['link-local-address']

            prefixes = [
                (ipv4_address['oper-address'].data + '/' + ipv4_pfxlen, 'n/a'),
                (ipv6_address['oper-address'].data + '/' + ipv6_pfxlen, ipv6_address['address-state'].upper()),
                (ipv6_ll_address['oper-address'].data + '/64', ipv6_ll_address['address-state'].upper()),
            ]
        except KeyError as e:
            if ('link-local-address' in str(e)):
                # system has no LLA
                prefixes = [
                    (ipv4_address['oper-address'].data + '/' + ipv4_pfxlen, 'n/a'),
                    (ipv6_address['oper-address'].data + '/' + ipv6_pfxlen, ipv6_address['address-state'].upper()),
                ]
            else:
                # there was no IPv4@ on the interface
                prefixes = [('-', 'n/a')]


        adm_state = "enable"
        try:
            adm_state = conn.running.get('/configure/router[router-name="'+router_instance+'"]/interface[interface-name="' + interface_name + '"]/admin-state').data
        except LookupError as e:
            # default value is "enable"
            pass

        port_id = 'n/a'
        try:
            port_id = conn.running.get('/configure/router[router-name="'+router_instance+'"]/interface[interface-name="' + interface_name + '"]/port').data
        except LookupError as e:
            if interface_name == "system":
                port_id = "system"
            # default value is "n/a"
            pass

        mode = 'network'
        try:
            mode = conn.running.get('/configure/port[port-id="' + port_id + '"]/ethernet/mode').data
        except LookupError as e:
            # default value is "n/a"
            pass
        except SrosMgmtError as e:
            pass

        result.append(
            RouterInterface(
                interface_name,
                prefixes,
                adm_state,
                interface_info['ipv4']['oper-state'].data,
                interface_info['ipv6']['oper-state'].data,
                port_id,
                mode,
                router_instance,
            )
        )
    return result

def main():
    conn = connect()
    base_router_interfaces = getRouterInterfaces(conn)
    print_table(base_router_interfaces)


if __name__ == "__main__":
    main()
