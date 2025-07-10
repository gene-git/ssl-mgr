=========
Changelog
=========

Tags
====

::

	2.2.0 (2024-03-29) -> 6.1.0 (2025-07-10)
	71 commits.

Commits
=======


* 2025-07-10  : **6.1.0**

::

                *Version 6.1 :*
                * New integrity check.
                  On each run *sslm-mgr* validates that the production directory is up to
                  date
                  and consistent with the current suite of certificates, keys and TLSA
                  files.
                  If not, it explains what the problem is and suggests possible ways to
                  proceed.
                  Note that the first run after updating to *6.1* it will
                  automatically re-sync production directory if necessary. No action is
                  required by you.
                * Keep certs and production certs fully synced.
                  Includes removing *next* directory from production after the *roll*
                  has happened and *next* is no longer needed. This change allows us to
                  check
                  that production is correctly synchronized. Earlier versions did not
                  remove any files from production, needed or not.
                * New dev option *--force-server-restarts*.
                * Add ability to specif the top level directory (where configs and outputs
                  are read from / saved to) via environment variable *SSL_MGR_TOPDIR*.
                * External programs are run using a local copy of *run_prog()* from
                  the *pyconcurrent* module.
                You can also install *pyconcurrent* which will ensure the latest
                  version is always used.
 2025-07-08     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2025-07-08  : **6.0.0**

::

                New **major version 6.0* released. Includes:
                    * PEP-8, PEP-257 and PEP-484 style and type annotations.
                    * Major re-write and tidy ups.
                    * Split up various modules (e.g. certs -> 5 separate crypto modules.)
                    * Ensure config and command line options are 100% backward compatible.
                    * Improve 2 config values:
                      Background: Local CAs have self-signed a root CA certificate which is
                      then used
                      to sign an intermediate CA cert.  The intermediate CA is in turn used
                      to sign
                      application certificates.
                      * ca-info.conf: Intermediate local CA entries.
                        * ca_type = "local" is preferred to "self" (NB both work).
                          "self" should still be used for self-signed root CAs where it
                          makes more sense.
                      * CA service config file for self-signed root certificate:
                        *  "signing_ca" = "self" is now preferred to an empty string (NB
                        Both work).
                      * These 2 changes are optional but preferred. No other config file
                      changes.
                    * Simplify logging code.
 2025-03-11     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2025-03-11  : **5.7.1**

::

                After latex update we needed to fix building latex pdf to avoid error
 2025-02-28     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2025-02-28  : **5.7.0**

::

                DANE update:
                  for port 25 tlsa records are generated for each MX record same as always.
                  But now, if port is not 25, then TLSA records are for each subdomain in
                  the x509 SAN domain list.
                  There is also a capability to specify this with additional elemein in the
                  dane_tls item which can be "MX" or "SANS"
                Expand dane tlsa example config file
 2025-02-09     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2025-02-09  : **5.6.0**

::

                Less logging to stdout when not verbose. Keep details in log file
                Increase default saved logs to 200k plus 4 backup files
                Avoid double log of cert expiration when renewing.
                  Once when checking and again when renewing
                fix: time_to_renew() now returns the expiration string and caller chooses to
                log or not
                small logging improvements
 2025-01-10     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2025-01-10  : **5.4.0**

::

                Time to cert expiration now shown with more granularity
 2024-12-31     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-12-31  : **5.2.0**

::

                Git tags are now signed.
                Add git signing key to Arch Package
                Bump python vers
 2024-12-16     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-12-16  : **5.1.0**

::

                Add support for certbot "--preferred-chain" flag in ca-info.conf
                  New config for letsencrypt CA : preferred_chain defaults to unset (uses LE
                  default).
                   e.g. to switch to newer ECC root set: ca_preferred_chain = "ISRG Root X2"
 2024-12-13     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-12-13  : **5.0.0**

::

                Bug Fix: Its not an error if copy_file(src, dst) when src non-existent.
                  => copying to production failed incorrectly if a tlsa file was missing
                  when none was needed/generated
 2024-11-27     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-11-27  : **4.9.0**

::

                Fix typo in dns server when separate server provided for specific domain(s)
                conf.d/ssl-mgr.conf - services can now be wildcard services (ALL or *)
                  Every file in group directory that is a service config will be included as
                  service
                add self signed wild card example
                Fix bug with sslm-info not showing IP addresses in SAN
 2024-10-21     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-10-21  : **4.5.0**

::

                 * New config variable : renew_expire_days_spread (default 0)
                   When set to value > 0, renew will happen between expiry_days ±spread
                   days.
                   Where spread days is randomly drawn from a uniform distribution between
                   -spread and spread.
                   Using this keeps the average renewal time the same but with multiple
                   certificates
                   this helps renewals not all fall on same day even if have same
                   expiration.
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-10-21  : **4.4.0**

::

                update Docs/Changelog.rst Docs/ssl-mgr.pdf
                use ipaddress instead of netaddr
                Improve messages; more compact
                Some lint picking
 2024-08-18     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-08-18  : **4.3.0**

::

                    New config option *post_copy_cmd*
                       For each server getting copies of certs may run this command on
                       machine on which sslm-mgr is running.
                       The command is passed server hostname as an argument.
                       Usage Example: if a server needs a file permission change for an
                       application user to read private key(s).
                       This option is a list of *[server-host, command]* pairs
 2024-08-17     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-08-17  : **4.2.0**

::

                X509v3 Extended Key Usage adds "Time Stamping"
                Changed sslm-dhparm to generate RFC-7919
                   Negotiated Finite Field Diffie-Hellman Ephemeral Parameters files - with
                   the default
                   now set to ffdhe8192 instead of ffdhe4096. User options -k overrides the
                   default as usual
                   NB push prod certs to all servers using: sslm-mgr dev -certs-prod
                   NB TLSv1.3 restricts DH key exchange to named groups only.
                openssl trusted certificates there is ExtraData after the cert
                   which has the trust data. cryptography.x509 will not load this so strip
                   it off.
                   see : https://github.com/pyca/cryptography/issues/5242
 2024-06-11     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-06-11  : **4.0.2**

::

                Tweak readme
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-06-11  : **4.0.1**

::

                Add netaddr as a dependency (used for having IP addresses in alt-names)
                Add couple of comments to end of readme about using self-signed certs
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-06-11  : **4.0.0**

::

                Bug fix: CA certs need to be marked as CA and set certificate signing
                ability
 2024-05-29     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-29  : **3.7.0**

::

                    Add comment to Readme about new self signed CA example
                    Tweak log message on cert expiration
 2024-05-28     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-28  : **3.6.0**

::

                    Skip writing tlsa file if woule be empty.
                    Be more tolerant of missing input
                    Add working example for self signed web server
 2024-05-26     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-26  : **3.5.0**

::

                bug fix with self signed root cert expiration not using sign_end_days in
                config
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-26  : **3.4.0**

::

                bugfix for self signed cert - fix argument typo
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-26  : **3.3.0**

::

                Avoid errors when missing servers
 2024-05-22     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-22  : **3.2.4**

::

                README updates
 2024-05-21     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-21  : **3.2.2**

::

                More readme updates
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-21  : **3.2.1**

::

                update readme
 2024-05-20     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-20  : **3.2.0**

::

                Tweak logging - more info about nameserver checks and visually tidier
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-05-20  : **3.1.1**

::

                Seems possible that letsencrypt dns-01 may not always use the apex domain
                    authoritative servers or perhaps their (secondary) check can lag more.
                    At least it seems that way lately.
                    We tackle this with the addition of 2 new variables to the top level
                    config:
                    See README : dns-check-delay and dns_xtra_ns.
                improve the way nameservers are checked for being up to date with acme
                challenges.
                    First check the primary has all the acme challenge TXT records. Then
                    check
                    all nameservers, including the *xtra_ns* have the same serial as the
                    primary
                Code improvements and cleanup in dns module.
                buglet whereby the cleanup code was incorrectly calling for dns nameserver
                validation.
 2024-04-23     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-04-23  : **2.5.0**

::

                Adjust for upcoming python changes.
                Some argparse options have been deprecated in 3.12 and will be removed in
                3.14
 2024-04-21     update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-04-21  : **2.4.0**

::

                Enhance non-dns restart_cmd to allow a list of commands. Useful for postfix
                when using sni_maps which must be rebuilt to get new certificates
 2024-03-29     remove duplicate depends in PKGBUILD
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-03-29  : **2.3.1**

::

                more little readme changes
                minor readme tweak
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-03-29  : **2.3.0**

::

                Add PKGBUILD depends : certbot and optdepends: dns_tools
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-03-29  : **2.2.1**

::

                update Docs/Changelog.rst
                update project version
                Fix typo in PKGBUILD
                update Docs/Changelog.rst Docs/ssl-mgr.pdf

* 2024-03-29  : **2.2.0**

::

                update cron sample file comment
                Initial Commit


