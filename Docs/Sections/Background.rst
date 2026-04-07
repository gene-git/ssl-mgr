.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Background:

**********
Background
**********

Groups & Services
=================

To keep things organized, data is partitioned into groups and services.

There are two types of groups: 

* Certificate Authorities (CAs)
* Apex Domains.

A CA can be an external Authority such as Letsencrypt or an internal / local one.

A local CA is structured similarly to an external one by having
a self-signed root certificate along with a companion intermediate cert(s) that
cert is signed by the root cert. Intermediate certs are then used to sign any
requested certificates.

Certificates are typically used by a server such as a web or email server. 
Each certificate is defined by a *service*. Certificates carry an apex domain
(e.g. example.com) but may have additional subdomains (sub1.example.com, sub2.example.com).
The full list of all these domains in a certificate is stored under Subject Alternative Names 
or SANS. 

An apex domain can have multiple certificates, where each certificate includes
all the subdomains along with the apex domain. All the desired details for each certificate
is provided in a *service* config file.


Certificate Authorities
-----------------------

The job of a CA is to take a Certificate Signing Request (CSR) and return a signed cert.

* Internal CA

  * Self-signed root certs are used solely to sign local intermediate certs.

  * Local intermediate certs are used to sign certs. The intermediates are signed by 
    a local self signed root. 

 Using internal certs are a good starting point when getting set up and exploring *ssl-mgr*.

* Letsencrypt CA

  When ready, using their test server, which is more generous with limits, is a good 
  way to prepare for the production. LE's test server is invoked by using the *-t*
  option. The *--dry-run* option may be helpful too.
 
  When all is working as desired, drop the test option and you're ready 
  to go into production.


Apex Domains
------------

An Apex domain is the *main* part of the domain with it's own DNS authority. 

If *example.com* has a DNS SOA record, then it would be the apex domain and any
of it's subdomain, such as *foo.example.com* would be a part of that apex domain. 
Whenever we deal with DNS, we (almost) always deal with the apex domain.

Each apex domain is a *group* and may have 1 or more certificates where each 
certificate is associated with 1 service.

Services
--------

Each service gets 1 certificate.

An apex domain may want/need different certs for different services. Each service has
one certificate.

An apex domain, for example, may have a mail service and a web service. Each of these has it's own
unique cert. Now, mail may use 2 certs, perhaps elliptic curve and RSA, then we would
simply have 2 services for mail. In this case lets call them *mail-ec* and *mail-rsa*
and lets call the web service *web-ec*. Its good to name services in a way thats
useful for administrator - it has no significance to the code other than the name must be
a good filename so cannot contain */* etc.

In the same vein, for self signed CA certs, we have 2 items - a *root* cert and an *intermediate*
cert where each belongs the special group *ca*. Again, each of these is a separate service.

Since each service has its own certificate, each has its own X509 name which describe
what it is. This includes things like Common Name, Alternative Names and organization.
In this case it includes info about the keys to be used and which entity
is provides the signed certificate. 

Each service has it's information provided by a service file.  It has all the information
needed to create keys and CSRs as well as certs.  This include key type, various *name* fields
along with which CA should be used.  The *name* fields are essentially *x509* Name [#x509-Name]_
fields. These include things like Common Name, Organization and so on.

.. [#x509-Name] x509 Name https://en.wikipedia.org/wiki/X.509

CSR (certificate signing request) contains the *subject* organiziation (thats the apex domain
org) information along with the public key. The private key is kept in a separate file. 
The CSR is sent to the CA which, all being well,  returns a (signed) certificate.

The resulting cert and certificate chain(s) are kept together with the key and CSR files.
A cert is signed by the *Issuer* and in addition to the signature contains the 
public key. The *chain* file contains the public key and x509 Name of the certificate issuer.

There are a couple of tools provided (*sslm-verify* and *sslm-info*) that make it 
easy to validate a certificate or display information about it. 
*sslm-info* works on all the *sslm-mgr* outputs : keys, csrs, certs, chains, fullchains and bundles.

Key/Cert Files
==============

* CSR (certificate signing request)

  Each certificate for is generated from its CSR which contains the
  public key. Public key is generated from the private key so there
  is no need to save a public key.
   
  A CSR is always used make a cert. This provides control as well as 
  consistency across CAs, be they self or other.
  The public key is in the CSR and also in the certificate provided and signed by the CA. 
  We support both RSA and Elliptic Curve (EC) keys. EC is strongly preferred.
  In fact, while RSA keys are still used they are only needed by ancient
  client software for browsers and email. That said, RSA is still in common 
  use for DKIM [#dkim]_ signing for some reason. We DKIM sign outbound mail with both RSA and EC.

* Cert 

  Each cert contains the public key which is signed by the CA. It carries the *subject* 
  apex domain name along with 'subject alternative names' or SANS. SANS allow a certificate to contain
  multiple domain or subdomain names. The *issuer*, which signed the certificate, has it's name 
  in the cert as well. Name in this context is an X509 name meaning, common name, organization,
  organization unit and so on.

* Certificate chains

  * **chain** =  CA root cert + Signing CA cert

    Signing CA cert is usually the CA Intermediate cart(s)
    Note that the root cert may or may not be included by CAs other than LE
    For those client chain = signing ca

  * **fullchain** = Domain cert + chain

  * **bundle** = priv-key + fullchain. 
      
    A bundle is just a chain made of the private key plus the fullchain. This is preferred 
    by postfix [#postfix_tls]_.

* Private key

  Also called simply the *key*. It is stored in a file with restricted permissions. 
  The companion public key can be generated from the private key. By always generating
  the public key from the private key, they are guaranteed to remain consistent.

Key, CSR and certificate files are stored in the convenient PEM format. Certificates use 
X509.V3 [#x509]_ which provides for *extensions* such as SANS which are critical to have. 
CSR files use *PKCS#10* [#pkcs]_ which can carry the same set of X509 extensions.

.. [#dkim] DKIM -> https://datatracker.ietf.org/doc/html/rfc6376
.. [#postfix_tls] Postfix TLS -> https://www.postfix.org/postconf.5.html#smtpd_tls_chain_files
.. [#x509] X509 V3 -> https://datatracker.ietf.org/doc/html/rfc5280
.. [#pkcs] PKCS#10 CSR -> https://www.rfc-editor.org/rfc/rfc2986

