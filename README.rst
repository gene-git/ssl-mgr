.. SPDX-License-Identifier: GPL-2.0-or-later

#######
ssl-mgr
#######

Certificate management tool. 

Note that the *Docs* directory contains the full PDF which includes details of the most
recent changes (*Docs/Changes-7.x.rst*). 

************
Key Features
************

* Handles creating new and renewing certificates

* Generates key pairs and Certificate Signing Request (CSR) to provide maximum control 

* Supports http-01 and dns-01 acme challenges

* Outputs DNS files for acme DNS-01 authentication as well as optioanal DANE TLSA files.
  These files are to be included by the apex domain zone file. This makes updates 
  straightforward.

* Uses certbot in manual mode to handle communication with letsencrypt, account tracking etc.

* Processes multiple domains and each domain each can have multiple certs.
  For example separate web and mail certs.

********
Overview
********

By way of background, I wrote this with 3 goals. Specifically to:

* Simplify certificate management - (i.e. automatic, simple and robust)
* Support *dns-01* acme challenge with Letsencrypt (as well as *http-01*)
* Support *DANE TLS*

The aim is to make things robust, complete and as simple to use as possible. 
Under the hood, make it sensible and automate wherever feasible. 

A good tool does things correctly while using it should be straightforward 
and as simple as possible; but no simpler.

In practical terms, there are only 2 common commands that are needed with *sslm-mgr*:

* **renew** - creates new certificate(s) in *next* : current certs remain in *curr*. 
* **roll** - moves *next* to become the new *curr*.

Once things are set up these can be run out of cron - renew, then wait, then roll.
Clean and simple. 

Strictly speaking, cert rolling is only needed when they are advertized 
via DNS (for example) and some time is required for things to flush through.  

In the first step, rolling advertized both old and new keys and keeps them 
available for an appropriate period of time; typically long enough for 
DNS info to propogate and DNS servers to update. 

In the second, and last, roll step, dns is updated to advertize only the new certs.

Changing to new certs without rolling can be problematic if some DNS servers 
still point to the older certs.

Without any loss of generality we always renew and then roll. The roll wait time
can always be set to 0 if no public keys are being advertized over DNS.

The **sslm-mgr --status** option gives 
a convenient summary of all managed certificates along with their expiration and 
time remaining time before renewal. 

The separate **sslm-info** program provides a 
convenient way to display information about keys, certs (or chains of certs), CSRs etc.

The **sslm-verify** tool checks if a cert is valid.

N.B. DNSSEC is required for DANE otherwise it is not needed. However, we do recommend using DNSSEC
and have made available the tool we use to simplify DNS/DNSSEC management [#dnstool]_.


.. [#dnstool] dns_tools : https://github.com/gene-git/dns_tools

DANE can use either self-signed certs or known CA signed certs. *ssl-mgr* makes it straightforward 
to create self-signed certs as well. 

However, in practice, it is safer to use CA signed certs for 
SMTP to reduce the chance of potential delivery problems in the event a mail server requires 
a CA chain of trust. 

We therefore recommend using CA signed certificates and therefore publishing DANE TLSA records using 
those certificiates. Each MX will have its own TLSA record.

While DANE can be used for other TLS services, such as https, in practice it is only used with email.

For convenience, there is a PDF version of this document in the Docs directory.

Note:

All git tags are signed with arch@sapience.com key which is available via WKD
or download from https://www.sapience.com/tech. Add the key to your package builder gpg keyring.
The key is included in the Arch package and the source= line with *?signed* at the end can be used
to verify the git tag.  You can also manually verify the signature

*****************
Important Changes
*****************

Version 7 brings some significant enhancements supporting Letsencrypt's upcoming short lifetime 
certs (45-day and 6-day) as well as *ACME profiles*. 

We revisited the *when to renew* a certificate decision so that we can sensibly handle 
short lifetime certs.

There are new config options for those wanting to customize it. In preparation for the
upcoming May 13, 2026 45-day cert availability, we request *tlsserver* profile by default.

Everything should work without change. However, there are a couple of optional config options
we **recommend** removing. 

Please see :ref:`Latest_Changes` for the details and explanation of which configs should
be removed if they are being used. 


****************
ssl-mgr: Details
****************

More details about *ssl-mgr* tools are available in the :ref:`More_Details` section.

