.. SPDX-License-Identifier: GPL-2.0-or-later

.. _Appendix:

########
Appendix
########

.. _Dealing with Possible Problems:

Dealing with Possible Problems
==============================

Once the configuration files are set up it can be helpful to start with self-signed CA root
certificate and a local CA intermediate certificate (signed by that root cert). Use the 
local intermediate cert to sign your application certificates.

Once this is all working then try using Letsencrypt CA. Upon successful completion
the *certs* directory holds all outputs including historical data (older certs and so on).

A subset of the output data is then copied to the production directory.
It may also be copied to remote servers if configs request that. After certs are 
updated and copied then the list of programs to run specified in the *post_copy_cmd* 
config variable will be run. 

If there is a problem for some reason, then updating production will be avoided
to minimize any production impact. It is conceivable that 
after some error conditions, the production cert directory could get out of sync.
Or a server reboot while production certs are being updated.

On any subsequent run after experiencing some error condition, 
When *sslm-mgr* starts, it detects if any production cert files are
out of sync. If so,  a warning is issued and production cert dirs are updated 
and servers are restarted.

Manual intervention should not be required but if you need it for some reason,
the *dev* option gives ability to force production resync and to restart
servers.

This can be done using dev options:

.. code-block:: bash

    sslm-mgr dev --force --certs-to-prod

to bring production back in sync. To restart the servers use:

.. code-block:: bash

    sslm-mgr dev --force-server-restarts

And you may alos want to renew the certs:

.. code-block:: bash

    sslm-mgr -renew

and wait the usual 2-3 hours and roll as usual:

.. code-block:: bash

    sslm-mgr -roll


Self Signed CA
==============

The *examples/ca-self* directory has sample how to do this. The CA has a self-signed root certificate
(*my-root*) along with an intermediate certificate (*my-int*) which is signed by the root cert. 
Other certs are then signed by the intermediate certificate.

The 2 public CA certs then need to be added to the linux certificate trust store. To do this copy
each cert as below and update the trust store:

.. code-block:: bash

   cp certs/ca/my-root/curr/cert.pem /etc/ca-certificates/trust-source/anchors/my-root.pem
   cp certs/ca/my-int/curr/cert.pem /etc/ca-certificates/trust-source/anchors/my-int.pem
   update-ca-trust

Since browsers do not typically use the system certificate store the same certs will need to be imported
into each browser. This can be dont manually in the GUI or using *certutil* provided by the *nss* package.
Modern browsers typically keep the certificates in a file called *cert9.db* which can be updated
using for example something like this (untested):

.. code-block:: bash

    cert9='<path-to>/cert9.db'
    cdir=$(dirname $cert9)
    certutil -A -n "my-int" -t "TC,C,TC" -i xxx/my-int/curr/cert.pem -d sql:$cdir

Please see *certutil* man pages for more info.

Sample Cron File
================

.. code-block:: bash

    #
    # Renew certs
    #  - certs renew (check) every Tue afternoon and roll 3 hours later
    #
    30 14 * * 2 root /usr/bin/sslm-mgr -renew
    30 17 * * 2 root /usr/bin/sslm-mgr -roll

    #
    # update dh parms:
    # will update if existing file is older than min age.
    # The default min age is 120 days. Use -a to change min age.
    #
    30 2 5 * 2 root /usr/bin/sslm-dhparm -s /etc/ssl-mgr/prod-certs


Config ca-info.conf
===================

.. code-block:: bash

    [le-dns]    # Used to sign client certs
        ca_desc = 'Letsencrypt: dns-01 validation'
        ca_type = 'certbot'
        ca_validation = 'dns-01'

    [le-http]    # Used to sign client certs
        ca_desc = 'Letsencrypt: http-01 validation'
        ca_type = 'certbot'
        ca_validation = 'http-01'

    [my-root] # To sign our own intermediate 'sub' certs
        ca_desc = 'My Self signed root : EC signs my intermediate certs'
        ca_type = 'self'

    [my-sub]  # Used to sign client certs
        ca_desc = 'My intermediate : EC signs client certs'
        ca_type = 'local'


.. _config-ssl-mgr:

Config ssl-mgr.conf
===================

.. code-block:: bash

    [globals]
        verb = true
        sslm_auth_hook = '/usr/lib/ssl-mgr/sslm-auth-hook'      # For certbot
        prod_cert_dir = '/etc/ssl-mgr/prod-certs'
        logdir = '/var/log/ssl-mgr/ssl-mgr/Logs'

        clean_keep = 5
        min_roll_mins = 90
        #
        # Letsencrypt profiles: classic, tlsserver, shortlived
        # NB classic is going away.
        #
        preferred_acme_profile = 'tlsserver'

        dns_check_delay = 240
        dns_xtra_ns = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '208.67.222.222']
        
        post_copy_cmd = [['example.com', '/etc/ssl-mgr/tools/update-permissions'],
                         ['voip.example.com', '/etc/ssl-mgr/tools/voip-checker']
                         ]
                         
    [renew_info]
        # target times to expiration when to renew
        target_90 = 30.0        # was renew_expire_days in globals section
        target_60 = 20.0
        target_45 = 10.0
        target_10 = 5.0
        target_6 = 2.0
        target_2 = 1.0
        target_1 = 0.5

        # random variability days (0 means no variability)
        rand_adj_90 = 3.0       # was renew_expire_days_spread in globals section
        rand_adj_60 = 0.0
        rand_adj_45 = 0.0
        rand_adj_10 = 0.0
        rand_adj_6 = 0.0
        rand_adj_2 = 0.0
        rand_adj_1 = 0.0


    #
    # Groups & Services
    #
    [[groups]]
        active=true
        domain='example.net'
        services=['web-ec']

    [[groups]]
        active=true
        domain = 'example.com'
        services = ['mail-ec', 'mail-rsa', 'web-ec']

    [[groups]]
        active=true
        domain = 'ca'
        services = ['my-root', 'my-sub']

    #
    # DNS primary provides authorized NS (name servers) and MX hosts of apex_domain
    # Must have at least one for acme dns-01
    #
    [[dns_primary]]
        domain = 'default'
        server = '10.1.2.3'
        port = 11153

    [[dns_primary]]
        domain = 'example.com'
        server = '10.1.2.3'
        port = 11153

    #
    # Servers
    #
    [dns]
        restart_cmd = '/etc/dns_tools/scripts/resign.sh'
        acme_dir = '/etc/dns_tool/dns/external/staging/zones/include-acme'
        tlsa_dirs = ['/etc/dns_tool/internal/staging/zones/include-tlsa',
                    '/etc/dns_tool/external/staging/zones/include-tlsa',
                    ]

        # restart trigger when dns (TLSA) zones have changed.
        depends = ['dns']

    [smtp]
        servers = ['smtp1.internal.example.com', 'smtp2.internal.example.com']
        # If using sni_maps
        #restart_cmd = ['/usr/bin/postmap -F lmdb:/etc/postfix/sni_maps', '/usr/bin/postfix reload']
        restart_cmd = '/usr/bin/postfix reload'
        svc_depends = [['example.com', ['mail-rsa', 'mail-ec']]]
        depends = ['dns']

    [imap]
        servers = ['imap.internal.example.com']
        restart_cmd = '/usr/bin/systemctl restart dovecot'
        svc_depends = [['example.com', ['mail-rsa', 'mail-ec']]]
    
    [web]
        servers = ['web.internal.example.com']
        restart_cmd = '/usr/bin/systemctl reload nginx'
        server_dir = '/srv/http/Sites'                  # Used for acme http-01 validation
        svc_depends = [['any', ['web-ec']]]

    [other]
        # these servers get copies of certs
        servers = ['backup.internal.example.com', 'voip.internal.example.com']
        restart_cmd = ''

Config Service : example.com/mail-ec
====================================

.. code-block:: bash

    #
    # example.com : mail-ec
    #
    name = 'Example.com Mail'
    group = 'example.com'
    service = 'mail-ec'

    #signing_ca = 'my-sub'
    #signing_ca = 'le-http'
    signing_ca = 'le-dns'
    renew_expire_days = 30

    # Include tls.example.com in zone file to use
    #  => [[port, proto, usage, selector, match], ...]
    dane_tls = [[25, 'tcp', 3, 1, 1]]

    [KeyOpts]
        ktype = 'ec'
        ec_algo = 'secp384r1'

    [X509]
        # X509Name details
        CN = 'example.com'
        O = 'Example Company'
        OU = 'IT Mail'
        L = ''
        ST = ''
        C = 'US'
        email = 'hostmaster@example.com'    # required to register with letsencrypt

        sans = ['example.com', 'smtp.example.com', 'imap.example.com', 'mail.example.com']

Directory tree structure
========================

Directory Structure. By default we only use EC keys, can add RSA if required.
We use 'ec' as a label to keep things clear and allow easy way to change to new
key types (RSA or other).

Input:

.. code-block:: bash

    conf.d/
        ssl-mgr.conf
        ca-info.conf
        
        example.com/
            mail-ec
            mail-rsa
            web-ec

        example.net/
            web-ec

        ca/
            my-root
            my-sub
        ...


Output - Final Production Certs:

.. code-block:: bash

    prod-certs/
        example.com/
            tlsa.example.com

            dh/
                dh2048.pem
                dh4096.pem
                dhparam.pem -> dh4096.pem
                ...
            mail-ec/
                curr/
                    privkey.pem
                    csr.pem
                    chain.pem
                    fullchain.pem
                    cert.pem
                    bundle.pem
                    tlsa.rr
                    info
            web-ec/
                ...
            ...

Output - Internal Data

.. code-block:: bash

    certs/
        example.com/
            tlsa.example.com

            mail-ec/
                curr -> db/date1
                next -> db/date2

                db/date1/
                    csr.pem
                    privkey.pem
                    cert.pem
                    chain.pem
                    fullchain.pem
                    bundle.pem
                    tlsa.rr
                cb/
                    [files used by cerbot]

            web-ec/
                curr -> db/date1
                next -> db/date2

                db/date1/
                    ...
                cb/
                    [files used by cerbot]

            .. other services

        example.net/
            ...

Installation
============

Available on
 * `Github`_
 * `Archlinux AUR`_

On Arch you can build using the provided PKGBUILD in the packaging directory or from the AUR.
To build manually, clone the repo and :

 .. code-block:: bash

        rm -f dist/*
        /usr/bin/python -m build --wheel --no-isolation
        root_dest="/"
        ./scripts/do-install $root_dest

When running as non-root then set root_dest a user writable directory

Dependencies
============

* Run Time :

=================== ==================================
 Package             Comment
=================== ==================================
 python              3.13 or later
 dnspython           
 cryptography
 dateutil
 lockmgr            Ensures 1 app runs at a time
 pyconcurrent       
 bash
=================== ==================================

* Building Package:

=================== ==================================
 Package             Comment
=================== ==================================
 git
 uv              
 uv-build
 rsync
 sphinx              Optional (build) docs:
 texlive-latexextra  Optional (build) docs aka texlive tools
=================== ==================================

Philosophy
==========

We follow the *live at head commit* philosophy as recommended by
Google's Abseil team [1]_.  This means we recommend using the
latest commit on git master branch. 


License
=======

Created by Gene C. and licensed under the terms of the MIT license.

 * SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>


.. _Github: https://github.com/gene-git/ssl-mgr
.. _Archlinux AUR: https://aur.archlinux.org/packages/ssl-mgr
.. _AUR pyconcurrnet: https://aur.archlinux.org/packages/pyconcurrent
.. _Github pyconcurrnet: https://github.com/gene-git/pyconcurrent

.. _Letsencrypt_Profiles: https://letsencrypt.org/2025/01/09/acme-profiles
.. _Letsencrypt_45: https://letsencrypt.org/2025/12/02/from-90-to-45
.. _Letsencrypt_Client_Auth: https://letsencrypt.org/2025/05/14/ending-tls-client-authentication,
.. _Letsencrypt_Root: https://letsencrypt.org/certificates/
.. _Letsencryt_Baseline: https://cabforum.org/working-groups/server/baseline-requirements/requirements


.. [1] https://abseil.io/about/philosophy#upgrade-support


