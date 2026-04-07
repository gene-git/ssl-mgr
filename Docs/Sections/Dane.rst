.. SPDX-License-Identifier: GPL-2.0-or-later

.. _DANE:

****
DANE
****

For DANE TLSA records, care must be taken to properly *roll* new keys. Key rolling 
ensures that the *next* key and the *curr* key are both advertised in DNS 
for some period. After some time the new key can be made *curr*. This waiting period
should be long enough to provide sufficient time for all DNS servers to pick up both old and new
new keys before DNS is changed to only show the new ones.
It's reasonable to wait 2 x the DNS TTL or longer.

After that wait time, the new (*next*) keys can be then be made available as the new *curr* ones.
Applications, mail really,  can now use the new keys since the world has both sets of keys.

Then DNS servers can then be updated again, this time with just the new (now *curr*) keys in the TLSA records. 
DANE key roll is similar to key roll for DNSEC.  DANE TLSA actually requires DNSSEC. 

DANE was designed as an alternative to third party certificate authorities like letsencrypt which
means its fine to used self signed or CA signed certs. While DANE could be used for web servers
to date it is really only used for email.

The companion *dns_tools* package takes care of all our DNSSEC needs [#dnstool]_:  

.. [#dnstool] dns_tools : https://github.com/gene-git/dns_tools

And I recommend using it to simplify the DNS refresh needed for validating
Letsencrypt acme challenges using *DNS-01* as well as for DANE TLSA.
A DNS refresh means resign zones (when using DNSSEC) and then restarting the primary dns server.

DANE TLSA records contain the public key, or a hash of that key, and thus need to be refreshed
whenever that key changes; this is the key roll. It also means that if the key is kept the same, then
the TLSA records aren't changing [#tlsa-1]_.  *ssl-mgr* has an option to re-use the public key
when certs are being renewed, and this allows the TLSA records to remain unchanged. 
In that case no key roll is needed until that key is changed. Some may find this useful. 

It basically means using the same certificate signing request, CSR, to get a new cert. The CSR contains
the public key associated with the private key. So if keys dont change CSR doesn't change either,
and the same CSR can be re-used.

However, I find *ssl-mgr* makes it so simple to renew with new keys, that
I don't see much point in reusing the old keys. Of course using new keys offers a security benefit.

.. [#tlsa-1] DANE can use either public key or the cert. Cert does change when it's reneweed even if the
   public key is unchanged. I believe pretty much everyone uses the public key not the cert in
   TLSA reords.

Note that each MX for the mail domain will have a TLSA record as required by the standard.

.. _DANE_TLSA_FIRST_USE:

DANE First Use - Caution
------------------------

**Important**: 

A cautionary note about the turning on DANE TLSA for the first time for an Apex domain. 

Do not include dane TLSA records in DNS zone files, until after the *roll*.

The very first time *DANE* is turned on, *tlsa* DNS records are created for *next*. 
The reason is, at this point there are no *tlsa* records for *curr* and the key/cert 
in *curr* is what mail server is using.

So if DNS is pushed out before the roll, these new *TLSA* records for *next* will be visible.
However, the mail servers are still using the key/certs from *curr*. Mail servers attempting to send 
mail inbound to your servers will be checking for the certs being advertized which are 
from *next*, and these are not yet being used.

After the roll, it is fine to update the DNS zone file to include the DANE TLSA records, 
because the mail servers are now using the key/certs from *curr* as advertized by the
*DANE* records.

Going forward after a renewal, there will be no issue. This is becuase both *curr* and *next* *TLSA* 
DNS records will both be advertized before the roll. Mail server is then using *curr* and
there is a DANE records advertizing the *curr* cert.

So, after activating DANE the very first time for an Apex domain, hold off actually including those
TLSA records in the zone file until after the *roll*. After the *roll,  the mail servers are using the
key/certs advertized in the DNS *DANE TLSA* records.

