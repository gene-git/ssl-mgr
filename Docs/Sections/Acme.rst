.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Acme_Challenge:

**************
Acme Challenge
**************

Letsencrypt uses Automated Certificate Management Environment (ACME)
and while our focus is on Letsencrypt there are other providers using ACME as well.

The protocol provides a mechanism for the CA to provide a signed certificate.
The way *ssl-mgr* works is by creating a Certificate Signing Request (CSR) which 
is sent to Letsencrypt which returns a signed certificate. The CSR and the cert
contain the public key. The companion private key is never shared.

Before the CA signs the certificate it validates that we have control over the Apex domain and 
any other subdomains that are part of the certificate. There a various ways the validation
occurs. 

One validation method uses a web server (the http-01 protocol) and another uses
DNS server (dns-01). The validation generally involves the CA sending a secret which is
then made available on the web server for the domain name being validated or available
on the DNS server for the domain. After the CA has verified the correct secret has been
posted on the web/dns server it then issues the certificate.

Using *DNS-01* to validate Letsencrypt acme challenges is done by adding the challenge TXT records
to DNS, signing the zones (if using DNSSEC) and pushing them out, so that 
the signing CA can subsequently check those DNS records match appropriately and then 
they provide the requested cert. 

While [#acme_val_challenge]_ can use either http-1 or dns-01; dns is preferred 
whenever possible.

.. [#acme_val_challenge] acme-val-challenge : https://letsencrypt.org/docs/challenge-types/

There is a new acme protocol expected to be available in 2026 called 
`dns-persist-01 <https://datatracker.ietf.org/doc/html/draft-ietf-acme-dns-persist-00>`_.
This is similar to dns-01 but instead of requiring validation on every renewal, the
idea is to have a long lasting, persistent, DNS record which can be re-used at renewal.
This should simplify and speed up renewals.

Note that in order to update DNS, an appropriate tool is needed. We use 
`dns_tools <https://github.com/gene-git/dns_tools>`_ for that purpose.

To make this as smooth as possible, *ssl-mgr* should run on the DNS signing server. 
This allows files with DNS records, acme challenges and
TLSA record files, to be written to accessible directories on same machine. 

A possible future enhancement may allow the dns signing server to be remote.

Note that DNS server refresh is also done after any DANE TLSA records are updated.


