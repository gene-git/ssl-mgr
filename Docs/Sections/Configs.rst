.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Configs:

************************
Configs: Getting Started
************************

*ssl-mgr* handles keys, certificate signing requests (CSR) and certs. 
It takes care of generating DANE TLSA DNS records should they be desired.
It reloads/restarts specific servers whenever needed. Each server has 
defined dependencies which trigger restarts whenever those dependencies have changed.

For example, a web server may depend on one or more apex domain certificates and 
will be restarted when any of those certs change.

It needs external support tools such as zone signing for DNSSEC and restarting
dns servers as well as reloading web or mail servers to ensure new certs are
picked up. These are provided via the top level config file. 

There is support for private/self-signed CAs and Letsencrypt CA. 

The first order of business is to create the config files that describe what
needs to be done. They specify everything needed to obtain one or more certificates
for one or more domains.

There are 3 kinds of configs.

**ssl-mgr.conf**

This is the top level config which has the list of active apex domains and for each
domain a list of services for that domain. Each service produces one certificate.

It also specifes the commands to be used to restart servers (e.g. web, mail)
and where to write any acme challenge files (web or dns) that needed to validate domain 
control to the issuing CA. 

Lastly it defines where the final (production) certificates are to be stored.

**service configs**

Each certificate to be issued for an apex domain for some service uses one configuration file. 
For example a service might be a mail server using elliptic curve algorithm where certificate is
issued by Letsencrypt.

The service configs reside in a directory under its apex domain.

**ca-info.conf**

Information about each Certifice Authority is defined in this file.


Sample configs in examples/conf.d can be used as a template to get started.


