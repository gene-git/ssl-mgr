Changelog
=========

**[5.0.0] ----- 2024-12-13** ::

	    Bug Fix: Its not an error if copy_file(src, dst) when src non-existent.
	      => copying to production failed incorrectly if a tlsa file was missing when none was needed/generated
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.9.0] ----- 2024-11-27** ::

	    Fix typo in dns server when separate server provided for specific domain(s)
	    conf.d/ssl-mgr.conf - services can now be wildcard services (ALL or *)
	      Every file in group directory that is a service config will be included as service
	    add self signed wild card example
	    Fix bug with sslm-info not showing IP addresses in SAN
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.5.0] ----- 2024-10-21** ::

	     * New config variable : renew_expire_days_spread (default 0)
	       When set to value > 0, renew will happen between expiry_days ±spread days.
	       Where spread days is randomly drawn from a uniform distribution between -spread and spread.
	       Using this keeps the average renewal time the same but with multiple certificates
	       this helps renewals not all fall on same day even if have same expiration.
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.4.0] ----- 2024-10-21** ::

	    update Docs/Changelog.rst Docs/ssl-mgr.pdf
	    use ipaddress instead of netaddr
	    Improve messages; more compact
	    Some lint picking
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.3.0] ----- 2024-08-18** ::

	        New config option *post_copy_cmd*
	           For each server getting copies of certs may run this command on machine on which sslm-mgr is running.
	           The command is passed server hostname as an argument.
	           Usage Example: if a server needs a file permission change for an application user to read private key(s).
	           This option is a list of *[server-host, command]* pairs
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.2.0] ----- 2024-08-17** ::

	    X509v3 Extended Key Usage adds "Time Stamping"
	    Changed sslm-dhparm to generate RFC-7919
	       Negotiated Finite Field Diffie-Hellman Ephemeral Parameters files - with the default
	       now set to ffdhe8192 instead of ffdhe4096. User options -k overrides the default as usual
	       NB push prod certs to all servers using: sslm-mgr dev -certs-prod
	       NB TLSv1.3 restricts DH key exchange to named groups only.
	    openssl trusted certificates there is ExtraData after the cert
	       which has the trust data. cryptography.x509 will not load this so strip it off.
	       see : https://github.com/pyca/cryptography/issues/5242
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.0.2] ----- 2024-06-11** ::

	    Tweak readme
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.0.1] ----- 2024-06-11** ::

	    Add netaddr as a dependency (used for having IP addresses in alt-names)
	    Add couple of comments to end of readme about using self-signed certs
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[4.0.0] ----- 2024-06-11** ::

	    Bug fix: CA certs need to be marked as CA and set certificate signing ability
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.7.0] ----- 2024-05-29** ::

	        Add comment to Readme about new self signed CA example
	        Tweak log message on cert expiration
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.6.0] ----- 2024-05-28** ::

	        Skip writing tlsa file if woule be empty.
	        Be more tolerant of missing input
	        Add working example for self signed web server
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.5.0] ----- 2024-05-26** ::

	    bug fix with self signed root cert expiration not using sign_end_days in config
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.4.0] ----- 2024-05-26** ::

	    bugfix for self signed cert - fix argument typo
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.3.0] ----- 2024-05-26** ::

	    Avoid errors when missing servers
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.2.4] ----- 2024-05-22** ::

	    README updates
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.2.2] ----- 2024-05-21** ::

	    More readme updates
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.2.1] ----- 2024-05-21** ::

	    update readme
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.2.0] ----- 2024-05-20** ::

	    Tweak logging - more info about nameserver checks and visually tidier
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[3.1.1] ----- 2024-05-20** ::

	    Seems possible that letsencrypt dns-01 may not always use the apex domain
	        authoritative servers or perhaps their (secondary) check can lag more. At least it seems that way lately.
	        We tackle this with the addition of 2 new variables to the top level config:
	        See README : dns-check-delay and dns_xtra_ns.
	    improve the way nameservers are checked for being up to date with acme challenges.
	        First check the primary has all the acme challenge TXT records. Then check
	        all nameservers, including the *xtra_ns* have the same serial as the primary
	    Code improvements and cleanup in dns module.
	    buglet whereby the cleanup code was incorrectly calling for dns nameserver validation.
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[2.5.0] ----- 2024-04-23** ::

	    Adjust for upcoming python changes.
	    Some argparse options have been deprecated in 3.12 and will be removed in 3.14
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[2.4.0] ----- 2024-04-21** ::

	    Enhance non-dns restart_cmd to allow a list of commands. Useful for postfix when using sni_maps which must be rebuilt to get new certificates
	    remove duplicate depends in PKGBUILD
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[2.3.1] ----- 2024-03-29** ::

	    more little readme changes
	    minor readme tweak
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[2.3.0] ----- 2024-03-29** ::

	    Add PKGBUILD depends : certbot and optdepends: dns_tools
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[2.2.1] ----- 2024-03-29** ::

	    update Docs/Changelog.rst
	    update project version
	    Fix typo in PKGBUILD
	    update Docs/Changelog.rst Docs/ssl-mgr.pdf


**[2.2.0] ----- 2024-03-29** ::

	    update cron sample file comment
	    Initial Commit


