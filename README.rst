.. SPDX-License-Identifier: GPL-2.0-or-later

#######
ssl-mgr
#######

*sslm-mgr* is a certificate management tool that helps automate key/certificate 
creation and renewal. It handles multiple certificates for one or more domains.

See the *Docs* directory for the complete PDF documentation.

A key pair is comprised of a private *key* and a *certificate* holding the public key.

************
Key Features
************

* Create new key/cert pairs 
* Renew existing ones.
* Generate key pairs using Certificate Signing Request (CSR) for maximum control.
* Supports http-01 and dns-01 acme challenges.
* Support of dns-persist-01 planned for 2026 after available in Letsencrypt.
* Outputs files for acme DNS-01 authentication with appropriate DNS TXT records.

  These are included in the apex domain zone file, making updates straightforward.

* Optional support to output DANE TLSA file for each Apex domain. 
  
  These are included in apex domain DNS Zone file.

* Uses certbot in manual mode to communicate with letsencrypt, account tracking etc.

* Processes multiple domains - each domain can have multiple certs.

  For example making separate certs for web and email servers.


**************
Recent Updates
**************

**7.7.0**

* Improve the the time to renew decision days.
  We now use a piece-wise linear function instead of piece-wise constant.
  For example, given 45 certs renew with 10 days to expiry and 90 certs with 30 days,
  a cert with expiration in between 45 and 90 would use a renew days target that 
  is linearly interpolated between 10 and 30 days.

**7.6.0**

* Fixes an issue where a 45 day cert with original days to expiration less than 45, (e.g. 44.5)
  was renewing with 5 days remaining instead of 10 days remaining. This was happening as the
  code was using the renewal target for 10 certs instead of 45 day certs.
  
* Self and Local signed certs: Remove outdated 90 floor on cert expiration.

* Add type support for post quantum mldsa, mlkem to avoid type check warnings.
  Were not using this types, but they are supported by python cryptography.

* Add .nvchecker.toml file (pkgctl version check)

* Modify the check script for pycodestyle leading to couple small style changes in code.


********
Overview
********

Secure communications often use private / public key pairs. The public key
for many cases is contained within a certificate (*cert*) which is signed by some
certificate authority (*CA*) and has an expiration date. 
While certs have expiration date, keys (private or private) do not. 

There are several known and *approved* CAs, such as Letsencrypt,
whose own certificates are known and trusted. Browsers for example have trust in them.
When a certificate is presented that has been signed by one of these CAs, then the
browser trusts that certificate as well. 

Obtaining a certificate from Letsencrypt and other CAs is done using 
the Automated Certificate Management Environment (ACME) protocol.

See :ref:`Acme_Challenge` for some background how CA certificates are validated.

Web and mail servers both use key/certs. Web servers have browsers and 
other clients and mail servers (mostly) have other mail servers as clients.

Letsencrypt is a CA service that provides signed certificates for these kinds of uses.
Their certificates have moderately short (and getting shorter) expirations and thus need
to be renewed periodically.

I wrote *ssl-mgr* with 3 goals. Specifically to:

* Simplify certificate management - (i.e. automatic, simple and robust)
* Support *dns-01* acme challenge with Letsencrypt (as well as *http-01*)
* Support *DANE TLS*

Creating and reenewing key/certs can be tricky. *ssl-mgr* strives to make things robust, 
complete, clean and as simple to use as possible.  
Under the hood, make it sensible (do the *right* thing) and automate wherever feasible. 

A good tool does things correctly while making using the tool as straightforward 
and simple as possible; but no simpler.

In practical terms, there are only 2 key commands needed with *sslm-mgr*:

* **renew** - creates new certificate(s) in *next* : current certs remain in *curr*. 
* **roll** - moves *next* to be the new *curr*.

The configuration files provide all the relevant information about the domains
and certificates needed.
After the configuration files are set up with the appropriate information 
then these commands can be run out of cron:

* renew, wait, roll.

Clean and simple. 

Rolling of certs is strictly only needed when certs are advertised 
via DNS (for example) and some time is required for DNS caches to flush through.  
This is true for DANE, since it provides certs via DNS *TLSA* records.

In the first roll step, both old and new keys are advertised and they are kept 
available (in DNS) for an appropriate period of time; typically long enough for 
DNS info to propogate and DNS servers to update. 

In the second, and last, roll step, DNS is updated to advertise only the new certs.

Changing to new certs without rolling can be problematic if some DNS servers 
still point to the older certs.

Without any loss of generality we can always renew and roll. If a roll is not 
needed, then the roll wait time can be adjusted to a small value, or even to 0. 


**N.B.** 

DNSSEC is required for DANE otherwise its not needed. However, we still recommend using DNSSEC
and made available the tool we use to simplify DNS/DNSSEC management [#dnstool]_.

**Important**

* When activating DANE for the first time it's important to only include DANE TLSA records
  after the *roll*. See :ref:`DANE_TLSA_FIRST_USE` for more detail. 


.. [#dnstool] dns_tools : https://github.com/gene-git/dns_tools

DANE can use either self-signed certs or *known* Certificate Authority (CA) signed certs. 
*ssl-mgr* makes it straightforward to create self-signed certs as well. 

The recommended way for creating and using your own certs is
to have your own self-signed CA which is then used to sign an *intermediate* certificate. 
The *intermediate* cert is what is then used to sign other certificates. This is the same
model used by well-known CAs as well. So it keeps it clean and simple to follow the same model.

While mail may use your own CA signed certs, , in practice, it is safer to use CA signed certs for 
to reduce the chance of delivery problems in the event a mail server requires 
a CA chain of trust. 

Therefore we therefore using CA signed certificates and publishing DANE TLSA records using 
those certificiates. Each MX will have its own TLSA record.

While DANE can be used for other TLS services, notably https, in practice it is only used with email.

Cert Information
----------------

**sslm-mgr --status** provides a convenient summary of all 
managed certificates along with their expiration and 
time remaining time before the next renewal. 

Sample output of *sslm-mgr --status --verb example.com:web-ec-self*:

.. code-block:: text

     web-ec-self
         curr         : expires: 2026-07-06 12:07:39+00:00 (  89 days + 23:59:07)
                      : issued : 2026-04-07 12:07:39+00:00 (   0 days + 00:00:52 ago. 90 day cert)
               issuer : CN=MySub-ec O=Example IT Department
              subject : CN=example.com
               pubkey : pubkey-secp384r1
                 sans : ['example.com', 'www.example.com']
             sig_algo : ecdsa-with-SHA384

The last two lines are included when *--verb* option is used.


File Information
----------------

While *sslm-mgr* interacts with the internal data, there are times when its useful
to find information about a certificate file.  The file can be a private key, 
a certificate (or chain of certs) or CSR.

**sslm-info <filename>** displays information about it's contents.

**sslm-verify** checks whether a cert is valid.  Sample output:

.. code-block:: text

    -------------------
        Certificate ** Verified **
    Certificate Info:
    Expires  : 2026-06-23 17:50:05+00:00 (  77 days + 05:24:38)
    Issued   : 2026-03-25 17:50:06+00:00 (  12 days + 18:35:20 ago. 90 day cert)
    Issuer   : CN=YE2,O=Let's Encrypt,C=US
    Pubkey   : pubkey-secp384r1
    Sig algo : ecdsa-with-SHA384


    -------------------
    Chain Info:
    Expires  : 2028-09-02 23:59:59+00:00 ( 879 days + 11:34:32)
    Issued   : 2025-09-03 00:00:00+00:00 ( 216 days + 12:25:26 ago. 1096 day cert)
    Issuer   : CN=Root YE,O=ISRG,C=US
    Subject  : CN=YE2,O=Let's Encrypt,C=US
    Pubkey   : pubkey-secp384r1
    Sig algo : ecdsa-with-SHA384

    Expires  : 2032-09-02 23:59:59+00:00 (2340 days + 11:34:32)
    Issued   : 2025-09-03 00:00:00+00:00 ( 216 days + 12:25:26 ago. 2557 day cert)
    Issuer   : CN=ISRG Root X2,O=Internet Security Research Group,C=US
    Subject  : CN=Root YE,O=ISRG,C=US
    Pubkey   : pubkey-secp384r1
    Sig algo : ecdsa-with-SHA384

    Expires  : 2032-09-02 23:59:59+00:00 (2340 days + 11:34:32)
    Issued   : 2025-09-03 00:00:00+00:00 ( 216 days + 12:25:26 ago. 2557 day cert)
    Issuer   : CN=ISRG Root X1,O=Internet Security Research Group,C=US
    Subject  : CN=ISRG Root X2,O=Internet Security Research Group,C=US
    Pubkey   : pubkey-secp384r1
    Sig algo : sha256WithRSAEncryption


Git Repo
--------

Please Note:

All git tags are signed with the arch@sapience.com (public) key that is available via WKD
or for download from https://www.sapience.com/tech. Add the key to your package builder openpgp keyring.

The key is also included in the Arch package and the source= line with *?signed* at the end of the line
can be used to verify the git tag.  You can also manually verify the signature as usual with
*git verify*.

*****************
Important Changes
*****************

**Version 7.4.0**

* DANE TLSA record now supports a time-to-live (TTL). It is specifed in the service file:
  
  dane_tls_ttl = 3600

  dane_tls = [[25, 'tcp', 3, 1, 1, 'MX']]

  If dane_tls_ttl is not set, it defaults to 1800 seconds (30 minutes).
  Earlier versions inherited the TTL for the DNS zone.


More details on changes are dound in :ref:`Latest_Changes`.


****************
ssl-mgr: Details
****************

More details about *ssl-mgr* tools are available in the sections :ref:`Acme_Challenge`, 
:ref:`Background`, :ref:`Renew_Roll`, :ref:`Dane`, :ref:`Configs` and
:ref:`Using_Tools`.

