.. SPDX-License-Identifier: GPL-2.0-or-later


.. _Latest_Changes:

Latest Changes
==============


**Version 7.0.0 :** (Major version with important changes)

**Enhancements** 

These are to support upcoming Letsencrypt changes. See: 

  * `Letsencrypt_45`_
  * `Letsencrypt_Profiles`_
  * `Letsencrypt_Root`_
  * `Letsencrypt_Client_Auth`_
  * `Letsencryt_Baseline`_

ACME profiles 
-------------

Letsencrypt offers (or will offer) 3 profiles:

=================== ===========================================================
 Profile             Description
=================== ===========================================================
 **classic**         the current 90-day cert (goes away at some point)
 **tlsserver**       new 45-day certs.
 **shortlived**      new 6-day certs.
=================== ===========================================================

See the Letsencrypt website for additional information.

*ssl-mgr* now requests the *tlsserver* profile by default. If unavailable it 
falls back to classic profile.

On May 13 2026, Letsencrypt will switch the *tlsserver* profile to 45-day certificates. 
At that time, *ssl-mgr* certs will be the 45-day certs, provided the profile has not been set 
to something other than *tlsserver*.

Please note that these certs will not only have half the expiration of current 90-day certs
but are also dropping a few fields. 

*tlsserver* profile certs will **not** provide:

  * A *Common Name* field 
    
    CN has been *not recommended* by the Baseline Requirements for several years now.

  * A *Subject Key Identifier*
    
    A SKID is *not recommended* by the Baseline Requirements.

  * A *TLS Client Auth Extended Key Usage*
    
    root programs are moving towards requiring “single-purpose” issuance hierarchies, where 
    every certificate has only a single EKU.
  
  * A *Key Encipherment Key Usage* for certificates with RSA public keys 
    
    This KU was used by older RSA-based TLS cipher suites, but is unnecessary with TLS 1.3.
    Please note that no certificate should be using RSA at this point. 

Root Certs
----------
    
  *tlsserver* and *shorlived* profiles are signed by new *Gen Y* root and intermediate certs.

  See the note below about removing the **ca_preferred_chain** config option.

ca_preferred_chain option
-------------------------

The *ca_preferred_chain* config option, specifies a root chain preference, remains 
supported by *ssl-mgr*. 

Stop using this CA config option the new "ISRG Root YE" root chain is available.
They will be available on or before May 2026. Consult the Letsencrypt website
for more information.

Until then you can: 

* leave it unset (Letsencrypt will use the X1 RSA root chain)
* set it to "ISRG Root X2"

  As soon as LE makes the new Gen Y root chain available, remove this setting. 
  You could set it to "ISRG Root YE" but that will be the default with the
  45-day certs that roll out on May 13 2026.  After that it definitely better to 
  let Letsencrypt determine the root chain to use, so remove the *ca_preferred_chain*
  option at that time.

Once Generation Y root and intermediate certs are available, 
letsencrypt will use them for the ACME *tlseserver* and *shortlived* profiles. 
    
These *Gen Y* root certs replace the older X2 (EC) and X1 (RSA) root certs.
Letsencrypt will use the *YE* root chain for EC certs and *YR* for RSA certs. 
We recommend only using EC certs today (no more RSA).

With the older 90-day *classic* profile, it was reasoable to prefer the *X2* root chain for
EC certs since the default was (and still as of writing this note) to use X1 (RSA).

ca_preferred_acme_profile option
--------------------------------

A new option in CA config file, *conf.d/ca-info.conf*.
Each CA item can now set the preferred profile. For example it may be
useful to have a second Letsencrypt item using a different acme profile 
or maybe a different validation mechanism (like dns-01 vs http-01).

* Can be set to one of the available ACME profiles.
* Since classic will go away, the choice is between *tlsserver* and *shortlived*  
* Defaults to *tlsserver* if not provided in the config.

In the short term, if really needed for some reason, you can request the *classic* profile.
But, at some point, this profile will no longer be supported by Letsencrypt.

Renew Timing
------------
  
The enhanced decision on when renew is based the certificate's original lifetime.

In order to handle shorter certificates we added fine grained control
over when a cert should be renewed based on the original certificate expiration.

See :ref:`config-ssl-mgr` for more detail about the new *[renew_info]* section that replaces
the 2 older variables: *renew_expire_days* and *enew_expire_days_spread*.
  
Example files have also been updated as well.

Please note that existing configs will continue to work (as usual). Any older 
variables will apply to 90+ day cert renewals if they are not already set in 
the new *[renew_info]* section. 

The defaults provide reasonable choices even for very short lived certs. 
Simply **remove** (or comment out) the 2 options in the [globals] section:

* **renew_expire_days**
* **renew_expire_days_spread**

If you're happy with the defaults, the *[renew_info]* section is completely optional.

Cert Information
----------------

Certificate information reported by *sslm-mgr -s* and *sslm-info* now includes the
lifetime. e.g. 45-day or 90-day.

License
-------
 
*ssl-mgr* now licensed under GPL-2.0-or-later.


.. _Github: https://github.com/gene-git/ssl-mgr
.. _Archlinux AUR: https://aur.archlinux.org/packages/ssl-mgr
.. _AUR pyconcurrnet: https://aur.archlinux.org/packages/pyconcurrent
.. _Github pyconcurrnet: https://github.com/gene-git/pyconcurrent

.. _Letsencrypt_Profiles: https://letsencrypt.org/2025/01/09/acme-profiles
.. _Letsencrypt_45: https://letsencrypt.org/2025/12/02/from-90-to-45
.. _Letsencrypt_Client_Auth: https://letsencrypt.org/2025/05/14/ending-tls-client-authentication,
.. _Letsencrypt_Root: https://letsencrypt.org/certificates/
.. _Letsencryt_Baseline: https://cabforum.org/working-groups/server/baseline-requirements/requirements


