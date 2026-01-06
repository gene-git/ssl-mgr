.. SPDX-License-Identifier: MIT

#############
Older Changes
#############

**Version 6.4 :**

* Bug fix where the state machine can lose track of changes that happened.

**Version 6.1 :**

* New integrity check.
 
  On each run *sslm-mgr* validates that the production directory is up to date
  and consistent with the current suite of certificates, keys and TLSA files.

  If not, it explains what the problem is and suggests possible ways to proceed.

  Note that the first run after updating to *6.1* it will 
  automatically re-sync production directory if necessary. No action is 
  required by you.

  For more details see :ref:`Dealing with Possible Problems`.

* Keep certs and production certs fully synced. 
  
  Includes removing *next* directory from production after the *roll* 
  has happened and *next* is no longer needed. This change allows us to check
  that production is correctly synchronized. Earlier versions did not
  remove any files from production, needed or not.

* New dev option *--force-server-restarts*.

* Add ability to specify the top level directory (where configs and outputs
  are read from / saved to) via environment variable *SSL_MGR_TOPDIR*.

* External programs are run using a local copy of *run_prog()* from 
  the *pyconcurrent* module.
  You can also install *pyconcurrent* which will ensure the latest
  version is always used. It is available in `Github pyconcurrnet`_ and 
  `AUR pyconcurrnet`_.

**Version 6.0 : Major Changes**

* PEP-8, PEP-257 and PEP-484 style and type annotations.
* Major re-write and tidy ups.
* Split up various modules (e.g. certs -> 5 separate crypto modules.)
* Ensure config and command line options are 100% backward compatible.
* Improve 2 config values: 

  Background: Local CAs have self-signed a root CA certificate which is then used 
  to sign an intermediate CA cert.  The intermediate CA is in turn used to sign 
  application certificates.

  * ca-info.conf: Intermediate local CA entries.
        
    ca_type = "local" is preferred to "self" (NB both work). 
    "self" should still be used for self-signed root CAs where it
    makes more sense. Intermediate are signed by root and
    are therefore not self-signed.

  * CA service config file for self-signed root certificate:
       
    "signing_ca" = "self" is now preferred to an empty string (NB Both work).

  * These 2 changes are optional but preferred. No other config file changes.

* Simplify logging code.


**Previous Changes:**

* Support Letsencrypt alternate root chain.

  Set via *ca_preferred_chain* option in *ca-info.conf* file (see example file).

  By default LE root cert is *ISRG Root X1* (RSA). Since it is standard to use ECC for 
  certificates, it is preferable to use LE *ISRG Root X2* (ECC) which is smaller and faster
  since less data is exchanged during TLS handshake.

  X2 cert is cross-signed by X1 cert, so any client trusting X1 should trust X2.
   
  Some more info here: `LE Certificates: <https://letsencrypt.org/certificates>`_ and `Compatibility <https://letsencrypt.org/docs/certificate-compatibility>`_.

* New config option *post_copy_cmd*

  For each server getting copies of certs may run this command on machine on which sslm-mgr is running.
  The command is passed server hostname as an argument.
  Usage Example: if a server needs a file permission change for an application user to read private key(s).
  This option is a list of *[server-host, command]* pairs. See :ref:`config-ssl-mgr`

* X509v3 Extended Key Usage adds "Time Stamping"

* Changed sslm-dhparm to generate RFC-7919
  Negotiated Finite Field Diffie-Hellman Ephemeral Parameters files - with the default
  now set to ffdhe8192 instead of ffdhe4096. User options -k overrides the default as usual

  NB If you manually update DH files in prod-certs, then push to all servers:

      sslm-mgr dev -certs-prod

  NB TLSv1.3 restricts DH key exchange to named groups only.

* In openssl trusted certificates there is ExtraData after the cert
  which has the trust data. cryptography.x509 will not load this so strip it off.
  see : https://github.com/pyca/cryptography/issues/5242

* Add a working example of self signed web cert in examples/ca-self.
  Create ca-certs (./make-ca) then generate new web cert signed by that ca.
  (sslm-mgr -renew; sslm-mgr -roll)

* letsencrypt dns-01 challenge may not always use the apex domain's
  authoritative servers or perhaps their (secondary) checks might lag more.
  We tackle this with the addition of 2 new variables to the top level config:
   
  * *dns-check-delay*. 

    Given in seconds, this causes a delay before attempting to validate that all authoritative servers 
    have up to date acme challenge dns txt records.
    Defaults to 240 seconds - this may well need to be made longer.
    Obviously, this does lead to longer run times - by design.

  * *dns_xtra_ns*. 

    List of nameservers (hostname or ip) which will be checked to have up to date acme challenge 
    dns txt records in addition to each apex domain authoritative nameserver.
    Default value is:

    dns_xtra_ns = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '208.67.222.222']

  * improve the way nameservers are checked for being up to date with acme challenges.
    First check the primary has all the acme challenge TXT records. Then check 
    all nameservers, including the *xtra_ns* have the same serial as the primary 

  * While things can take longer than previous versions, teting to date has shown it 
    to be robust and working well with letsencrypt.



.. _AUR pyconcurrnet: https://aur.archlinux.org/packages/pyconcurrent
.. _Github pyconcurrnet: https://github.com/gene-git/pyconcurrent

