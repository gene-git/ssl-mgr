Changelog
=========

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


