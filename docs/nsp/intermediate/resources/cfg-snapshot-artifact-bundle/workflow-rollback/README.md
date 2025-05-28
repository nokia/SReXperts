## LSO Operation - Rollback NE Config

> Copyright **2024 NOKIA**<br>
> Licensed under the BSD 3-Clause License.<br>
> SPDX-License-Identifier: BSD-3-Clause

### Benefits
- Rolling back the configuration to the snapshot without reboot
- Does not require FTP Mediation while using MDC RESTCONF
- Extensible for NETCONF/gRPC devices (including 3rd party vendors)

### Disclaimers
- For education/research purposes only
- Works for MD SROS devices only
- Not designed for scale/performance (check WFM best-practices)