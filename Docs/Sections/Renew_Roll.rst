.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Renew_Roll:

******************
Renewing & Rolling
******************

*ssl-mgr* keeps and manages 2 versions of every set of data. Each data set 
consists of certificates, keys, Certificate Signing Requests (CSRs) and dane tlsa records. 

One version of the data holds the current (or *curr*) set and the other has the *next* set.
*curr* are those currently in use while *next* are those that are on deck to become 
the next current set.

Key rolling is standard practice and should be familiar to those who have implemented *DNSSEC* for example. 
A *roll* provides a robust method to update keys/certs with new ones in a way that ensures nothing breaks.

For some uses, the current key/cert is advertised in DNS. After creating new keys/certs, DNS is then upated
to advertise both the current and the newly created next ones. 

An appropriate amount of time needs to pass with both current and next in DNS before doing the second 
phase of the *roll*. 
This gives the time needed for DNS servers to refresh. Once refreshed, the DNS servers have both 
the current and the next set of keys/certs.

After sufficient time, update a second time, after which only the new keys (the new current ones) 
are advertised in DNS.

A *roll* is required for *DNSSEC* keys (managed elsewhere) and for *DANE* which *ssl-mgr*
is responsible for.

Without any loss of functionality and to keep things nice and simple, we require 
every update to use a key roll. 

Again, a *roll* is required for *DANE TLS* but is not needed for things such as web server 
certificate update. 

If you are not advertizing certificate info using DNS servers (e.g. DNSSEC, DANE) 
then there is no need have much or even any delay between making a new certificate
using *-renew* and doing the *-roll*.

In this case, you can set the config variable *min_roll_mins* to **0** minutes.
The default min roll time is 90 minutes. And if automating (via cron or similar) then
you can also use do the *roll* immediately after the *renew* as well.
In cron you could have roll set to run 1 minute after the renew.

If you have DANE, then it is important to have an appropriate delay after the *renew* before 
doing the *roll*.

Also, you are always have control and, should it ever be needed, you can do 
whatever you choose.

e.g. Using *-f* option with *sslm-mgr* will force things to happen (a roll or create new certs and so on.)

Curr & Next
===========

These are kept in directories that contain different versions of the same set of files. 
Of course *next* has newer versions. For example for the group *example.com*
and the service *web-ec* their output directories would be:

.. code-block:: bash

    certs/example.com/web-rc/curr/
    certs/example.com/web-rc/next/

In order of creation these are:

=============   ============================================================
 File            What
=============   ============================================================
privkey.pem     the private key
csr.pem         certificate signing request
cert.pem        certificate
chain.pem       CA root + intermediate certs
fullchain.pem   Our cert.pem + CA chain
bundle.pem      Our privkey + fullchain
tlsa.rr         Optioanl Dane TLSA records
info            Contains date/time when next was rolled to curr (curr only)
=============   ============================================================

Once config is setup, a cron/timer to run *renew* followed by *roll* 2 or 3 hours later
should take care of everything. Can be run daily or weekly. 

The *curr/next* directories are copied to the production directory, 
as specified in *conf.d/ssl-mgr.conf* by the variable *prod_cert_dir*.
This directory can be copied to whatever servers need key/cert access.

Diffie-Hellman Parameters
=========================

The tool *sslm-dhparm* generates Diffie-Hellman parameters.
This too can be added to be run by cron.

By default *sslm-dhparm* only generates new parameters if they are more than 120 days old, or absent.
This can therefore be run weekly without issues. 

Note: The new, preferred and now default DH parameters are based on the `rfc_7919`_ 
*finite field* pre-defined named groups. 
The default is *ffdhe4096*. Pre-defined named groups only need to be generated once 
and *sslm-dhparm* will only generate them if absent. 

Strictly these don't need to be in cron, but its convenient to 
have the program check and create DH parameters should the file be missing. May
happen occasionally after adding new domain.

.. _rfc_7919: https://datatracker.ietf.org/doc/html/rfc7919

The 6 month default refresh, ony applies for non RFC-7919 params, and is recommended because 
it can be a bit time consuming to generate them.  Actual time varies with key size. 

When using a pre-defined named group (e.g. *ffdhe4096*), it is very quick to
produce and tool simply checks if file exists without any age requirement. These
are only created once.

Sample cron files are provided in the examples directory.

