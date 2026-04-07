.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Using_Tools:

*************************
Using the Tools : Details
*************************

Once the config files are set up then the tools can be used to do the real work.

The primary tool for generating and managing certificates is *sslm-mgr*.  As usual, help 
is available with the *-h* or *--help* option.

The 2 most frequently used options are *renew* and *roll*. 

There are some additional options that give a bit more control, in case
its ever needed.  These are discussed in detail below. 
For example the *-f* or *--force* option does what the name suggests. 
So 

.. code-block:: bash

   sslm-mgr -f -renew

will force a cert to be renewed even if its not yet time to do so.

There is also *dev* mode. This provides access to some lower lever tasks. 
This should seldom, if ever, be needed. In case you do, it is activated by 
by adding *dev* command as the first argument.

For example to get help for dev mode:

.. code-block:: bash

   sslm-mgr dev -h

The tools in the package include:

===================     ===========================================================
Tool                    Purpose
===================     ===========================================================
sslm-auth-hook          internal - used with certbot's manual hook option
sslm-dhparm             generates Diffie Hellman paramater file(s)
sslm-info               displays info about cert.pem, csr.pem, chain.pem, privkey.pem,  etc
sslm-mgr                primary tool for certificate management
sslm-verify             verifies any cert.pem file using the public key from chain.pem
===================     ===========================================================


sslm-mgr options
===============

As already mentioned, once configs are set up and running, then all that's 
needed is to run:

.. code-block:: bash

    sslm-mgr -renew

which will check get new certs, if it's time to renew. A couple of hours later make those certs
live by doing:

.. code-block:: bash

    sslm-mgr -roll


sslm-mgr options
----------------

Has 2 modes - a *normal* mode and a developer or *dev* mode. In both cases, 
the groups and services are read from the same config files.  
Some values *can* be overridden from the command line. 

To specify a group and service(s) on the command line use the format:

.. code-block:: none

   sslm-mgr ... <group-name>:<service_1>,<service_2>,...

For example, for a domain with multiple services, you can limit
to one or two services using:

.. code-block:: bash

   sslm-mgr -s example.com:mail-ec
   sslm-mgr -s example.com:mail-ec,mail-rsa

Help command for *sslm-mgr* :

.. code-block:: text

   sslm-mgr -h
   usage: /usr/bin/sslm-mgr [-h] [-clean-all] [-clean-keep CLEAN_KEEP] [-d] [-dns] [-f] [-n] [-r] 
                         [-renew] [-roll] [-roll-mins MIN_ROLL_MINS] [-s] [-t] [-v]
                         [grps_svcs ...]
 
    
    SSL Manager

    positional arguments:
      grps_svcs             List groups/services: grp1:[sv1, sv2,...] grp2:[ALL] ... 
                            (default: from config)

    options:
        -h, --help            show this help message and exit
        -clean-all, --clean-all
                                Clean up all grps/svcs not just active domains
        -clean-keep, --clean-keep CLEAN_KEEP
                                Clean database dirs keeping newest N (see --clean-all)
        -d, --debug           debug mode : print but dont do it
        -dns, --dns-refresh   dns: Use script to sign zones & restart primary
                                See config dns.restart_cmd
        -f, --force           Forces renew / roll / prod check
        -n, --dry-run         Letsencrypt --dry-run
        -r, --reuse           Reuse curr key with renew.tlsa unchanged if using selector=1 (pubkey)
        -renew, --renew       Renew keys/csr/cert keep in next (config renew_expire_days)
        -roll, --roll         Roll Phase : Make next the new curr and copy to production
                                Refresh dns if needed
        -roll-mins, --min-roll-mins MIN_ROLL_MINS
                                Only roll if next is older than this (config min_roll_mins)
        -s, --status          Display cert status. With --verb shows more info
        -t, --test            Letsencrypt --test-cert
        -v, --verb            More verbose output



When more control is needed then *dev* mode offers the above commands plus few more.
To see developer help:

.. code-block:: text

   # sslm-mgr dev -h
    usage: /usr/bin/sslm-mgr (as above plus)
                [-cert] [-certs-prod] [-copy] [-csr] [-fsr] [-keys] [-ntoc] 
                [grps_svcs ...]

    SSL Manager Dev Mode

    positional arguments:
        grps_svcs    List groups/services: grp1:[sv1, sv2,...] grp2:[ALL] ... 
                     (default: see config)

    options:
        ... same as above plus:

        -cert, --new-cert     Make new next/cert
        -copy, --copy-csr     Copy curr key to next (used by --reuse)
        -csr, --new-csr       Make next CSR
        -fsr, --force-server-restarts
                              Forces server restarts even if not needed
        -keys, --new-keys     Make next new keys
        -ntoc, --next-to-curr Move next to curr



Configuration Files
===================

Sample configs are show in Appendix :ref:`Appendix` and the files
are provided in *examples/conf.d* directory.

When setting for the first time, up its may be helpful to start by creating a self 
signed CA and use that.  
When you're ready, change the signing CA to Letsencrypt (LE) and run against the 
LE test-cert server by using

.. code-block:: bash

   sslm-mgr --test 

You may also use the Letsencrypt *--dry-run* option.

Once that is working then you switch to the normal LE server by dropping the
test option.

Config files are located in *conf.d*. There are 2 shared configs and
one config for each group/service.  Service configs files reside under 
their *group* directory.

The top level configs are *ssl-mgr.conf* and *ca-info.conf* which are used for 
all groups and services.

*ssl-mgr.conf* is the main config file and we'll go over it in detail.
It contains the list of domains and their services. 

Groups can be marked active (active = true). In inactive group is not processed.
*sslm-mgr* can optionally have 1 or more groups and services provided on the command line.
Any groups/services specified on the command line are the only ones that are run.

*ca-info.conf* is a list of available CAs. Each CA name can be referenced 
in the service configs to determine which CA is to provide the signed cert.

As explained earlier, there are 2 kinds of groups: *CA*s and *Apex Domain* groups. 
The *CA* group is for self created CAs and an *Apex Group* contains 1 more services
from which a key/certificate pair are to be created.

It is convenient to name services for their purpose (mail, web etc)
and also for any characteristics of the certificate,  such key type (RSA, Elliptic Curve)
and sometimes by the CA name as well.

Each service config resides under its group:

.. code-block:: text

     conf.d/<group>/<service>

This file describes the organization and details for this one service. It specifies 
which CA is to sign the certificate as well as any DANE TLS [#TLSA]_ info needed to generate
TLSA records.

.. [#TLSA] TLSA https://datatracker.ietf.org/doc/html/rfc6698

N.B. Each service is to be signed by the designated CA.
     If you want 2 certs signed by 2 different CAs, e.g. both self and letsencrypt,
     then each would have it's own distinct service name and config file.

     E.g. mail-self and mail-le.
     For each domain, the TLSA records for all services are aggregated into a single
     file, tlsa.rr which can be included by the DNS server apex zone file.

N.B.
    Letsencrypt signing the same CSR counts towards their limits independent
    of validation method used (http-01 or dns-01). 


Service Config
--------------

Info for each service to create it's cert. Each domain may have
separate certs for different services (mail, web, etc). Each service must therefore
have it's own unique config file. 
Its good practice to use separate certs for each different use cases, to help mitigate 
any impact of key related security issues.

Each config provides:

* Organization info (CN, O, OU, SAN_Names, ... )
* name, org, service (mail, web etc)
* Which CA should will be requested to sign this cert
  + validation method). Self signed dont need a validation method.
  + Letsencrypt, for example, allows http-01 and dns-01 as validation methods.
* DANE TLS info - list of (port, usage, selector, match) - e.g. (25,3,1,1)
* Key type for the public/private key pair

Output
======

All generated data is kepy in a dated directory under the *db* dir and links are provided
for *curr* and *next* 

* curr -> db/<date-time>
* next -> db/<date-time>

After a cert has been successfully generated, each dir will contain :

=============   ============================================================
 File            What
=============   ============================================================
privkey.pem     private key
csr.pem         certificate signing request
cert.pem        certificate
chain.pem       root + intermediate CA cert
fullchain.pem   cert + chain
bundle.pem      privkey + fullchain
tlsa.rr         Dane TLSA records for this service (if any)
info            Contains date/time when next was rolled to curr (curr only)
=============   ============================================================

The bundle.pem file, which has the priv key, is preferred by postfix to provide atomic udpate
and avoid a potential race during updates.
Such a race is conveivable if key and cert are read from separate files.

In addition there are the acme challenge files. The *ssl-mgr.conf* file specifies where
these files are to be written. 

DNS-01 Validation
-----------------

For dns-01 the location is specified as a directory:

.. code-block:: text

    [dns]
        acme_dir = '...'

The acme challenges will be saved into a file under *<acme_dir>* with apex domain name as suffix:

.. code-block:: text

   <acme_dir>/acme-challenge.<apex_domain>

The format of the DNS resource record is per RFC 8555 [#rfc_8555_dns]_ spec.
The challenge file should be included by the DNS zone file for that apex domain.
Once the challenge session is complete, the file will be replaced by an empty file,
which ensures that there are no errors including it in the domain zone file.

HTTP-01 Validation
------------------

For http-01 validation the location is specified by *server_dir* directory:

.. code-block:: text

    [web]
        server_dir = '...'

The individual challenge files, one per (sub)domain will be saved in a file following 
RFC 8555 [#rfc_8555_http]_ spec:

.. code-block:: text

   <server_dir>/<apex_domain>/.well-known/acme-challenge/<token>

.. [#rfc_8555_dns] DNS-01 Acme Challenge URI -> https://datatracker.ietf.org/doc/html/rfc8555#section-8.4
.. [#rfc_8555_http] HTTP-01 Acme Challenge URI -> https://datatracker.ietf.org/doc/html/rfc8555#section-8.3

If the web server is not local then ssh will be used to push the file to the remote server.

**N.B.** In all cases please ensure that the process has appropriate write permissions.

DANE-TLSA DNS File
------------------

If DANE is active for any service, then the TLSA records for that service are saved 
under *certs/<apex-domain>/<service>/tlsa.rr*. All service TLSA records for each apex domain
are then aggregated under *certs/<apex-domain>/tlsa.<apex-domain>*.

The apex domain TLSA file is then copied to one or more 
directories specified in the *[dns]* section of *ssl-mgr.conf*. 

This file is what can be included in the DNS zone file for that apex domain.

.. code-block:: text
    
   [dns]
        ...
        tlsa_dirs = [<tlsa_1>, <tlsa_2>, ...]

Each directory, *<tlsa_1>*, *<tlsa_2>* etc, will be populated with one file per apex_domain 
where each file contains the TLSA records for that domain. Each apex domain tlsa file will be
named:

.. code-block:: text

   tlsa.<apex_domain> 

Each file should be included by the DNS zone file for that apex domain.

**N.B.** Mail server needs a TLSA record for each key/certificate is used. If, for example,
postfix is set up to use either *RSA* or *EC* certs, then you **must** provide a TLSA record
for both of them. And there must be record for the apex domain as well as every MX host.

We determine the MX hosts from DNS lookup of the apex domain.



Service Config for TLSA
=======================

The service config allows DANE to be specified.

The input field takes the form of a list, one item per port:

.. code-block:: bash

   dane_tls = [[25, 'tcp', 3, 1, 1], [...], ...]

Each item has port (25 here), the network protocol (tcp) along with *usage* (3), *selector* (1)
and *hash_type* (also 1).

You should use (3,1,1).

The dane records normally contain the current TLSA records. During rollover
they contain both current and next ones, and after rollover completes, and 
next becomes current then we're back to the normal case with only current TLSA records.

Each apex domain has it's own file of TLSA records, *tlsa.<apex_domain>*.

The *ssl-mgr.conf* DNS section also specifies where these DNS TLSA record files should be
copied to - so that the DNS tools can include them in the apex domain zone file.

The best way to handle the dane resource records is by using $INCLUDE in dns zone file
to picks up *tlsa.<apex_domain>* file. 

DNS server is refreshed (i.e. zone files signed and primary server is restarted)  whenenever 
a dane tlsa file changes.

The TLSA records change when the private key is updated (leading to change in the hash itself)
or when the dane-info is changed (e.g. change of ports or other dane info). It certainly
changes after a *renew* builds new keys/certs in *next* and after *roll* when 
the new *curr* is updated.

For doing rollover properly, order is important. 

.. code-block:: bash

  curr ⟶  curr + next ⟶   DNS

After 2xTTL or longer:

.. code-block:: bash

  next ⟶  curr ⟶   update mail server ⟶   refresh DNS

*sslm-mgr* takes care of this.

While it is true that reusing a key, means not having to deal with key rolloever as often,
that only helps when doing things manually. And in fact even doing it manually, doing things
less frequently may mean mistakes are more likely. There is also a small security reduction
obviously in reusing a key.

When things are automated, as here with *sslm-mgr* taking care of everything, then there is little
benefit to key reuse. So we support it, but we recommend just renew and roll and all will be fine :)

Certbot: Notes
==============

A few notes on certbot and how we're using it.

In addition to the database directory (*db*) there is also a *cb* dir which
is provided to certbot. Certbot uses to to keep letsencrypt accounts. Each group-service
has its own everything - this includes it's own certbot *cb* and thus separately registered
LE (Letsencrypt) account for each service.

We are using cerbot in manual mode. This gives us a lot of control and allows us to 
use our own generated CSR as well as to specify
where the resulting cert and chain files get stored. 

When sending a CSR with apex domain plus sub-domains, each (sub)domain gets a challenge and
each challenge must be validated by LE before cert is issued. Challenges can be validated 
by acme http-01 or dns-01. Wildcard sub-domains (\*.example.com) can only be validated using dns-01.

Certbot sends each challenge to a *hook* program. The *hook* program is called once per challenge.
Information about the challenge and which sub-domain are passed to the *hook* program in 
environment variables. Env variables also tell the program how many more challenges remain to 
be sent. Once all the challenges have been delivered - and only after the *hook* program returns - 
LE will then seek to validate all of the acme challenges, whether http or dns validation is
being used.

This is actually really good - it means that we can push all the challenges out - and wait for
every DNS authoritative name server to have the TXT records before allowing the hook to return
once it has every acme challenge.

In older versions of certbot, validation took place after each sub-domain challenge, and for DNS
that meant dns refresh - wait for NS to udpate - LE checks and sends next challenge.
This could potentially very long wait times - I read of some folks waiting many hours. Now with
the new way as described above, whether DNS or HTTP challenge, it takes only seconds or minutes.

It seems to me that LE checks directly with each authoritative NS, which is the most efficient
way to check - rather than waiting on some random recursive server to get updated.


sslm-mgr application
====================

Usage
-----

To run - go to terminal and use :

.. code-block:: bash

   sslm-mgr --help

Config File Location
--------------------

The configuration file for ssl-mgr is chosen by checking for
as the first directory containing a *conf.d* directory from the 
list of *topdir* directories:

.. code-block:: text

   <SSL_MGR_TOPDIR>
   ./ 
   /etc/ssl-mgr/

Where the directories are checked in order and *<SSL_MGR_TOPDIR*> 
is an environment variable that can be set to take preference.

The config files are located in *topdir/conf.d/* and certificates, 
key files and so on are saved under *topdir/certs*.

For example if there environment variable is not set and the directory
*./conf.d* exists, then it becomes the top level directory. And all
configuration files reside under *./conf.d*.  

.. sslm-mgr-opts:

Log Files
=========

Logs are found in the log directory specified by the global config variable:

 .. code-block:: bash

    [globals]
        ...
        logdir = 'xxx'

There are 3 kinds of log files in the log directory. 

* *<logdir>/sslm*: General application log
* *<logdir>/cbot*: Application log while interacting with letsencrypt via certbot.
* *<logdir>/letsencrypt/letsencrypt.log.<N>*: Letsencrypt log provided by cerbot.


.. _Github: https://github.com/gene-git/ssl-mgr
.. _Archlinux AUR: https://aur.archlinux.org/packages/ssl-mgr
.. _AUR pyconcurrnet: https://aur.archlinux.org/packages/pyconcurrent
.. _Github pyconcurrnet: https://github.com/gene-git/pyconcurrent


