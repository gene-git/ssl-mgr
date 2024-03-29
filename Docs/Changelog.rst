Changelog
=========

**[2.3.0] ----- 2024-03-29** ::

	    update project version
	    Add PKGBUILD depends : certbot and optdepends: dns_tools
	    update Docs/Changelog.rst


**[2.2.1] ----- 2024-03-29** ::

	    update project version
	    PKGBUILD - update _gitname
	    update Docs/Changelog.rst


**[2.2.0] ----- 2024-03-29** ::

	    update project version
	    comments in cron file
	    update requirements/depends
	    readme ...
	    tweak readme some
	    tweak log for server reload/restart with 1 extra space
	    Tweak README a little
	    fix rst in README
	    update Docs/Changelog.rst


**[2.1.0] ----- 2024-03-22** ::

	    update project version
	    Reduce stdout log verbosity (mostly from dns restart script output)
	    Add log line for each server/service restart : dns, imap, smtp etc
	    update Docs/Changelog.rst


**[2.0.0] ----- 2024-02-19** ::

	    update project version
	    Add support of RFC-7919 pre-defined dh parameters.
	      Default changed from generated 2048 bit to pre-defined ffdhe4096
	    Remove Group: leader form group task message output.
	    Update package description
	    remove our domain name from example config.
	    Tweak README
	    Update example config with restart_tool -> restart_cmd change for dns server
	    remove debug
	    Bugfix: DNS restart - change config to use restart_cmd for all server sections. dns was using restart_tool which broke dependency check for DNS restart at end of renew and roll
	    Bug - cbot/sign_cert missed name change org -> svc
	    sslm-dhparam now defaults to 2048 bit (see openssl cookbook)
	    readme ...
	    tweak comment in example/crons
	    readme - change comment in cron example
	    readme ...
	    readme cont ...
	    update Docs/Changelog.rst


**[1.9.0] ----- 2023-11-26** ::

	    update project version
	    Add locking to sslm-mgr to prevent mishap if admin and cron overlap
	    update Docs/Changelog.rst


**[1.8.5] ----- 2023-11-25** ::

	    update project version
	    config - after migrating globals section, remove from dictionary
	    Tidy examples
	    Put ssl-mgr.conf globals in their own section.
	      This protects against problems if global variable happens to be put below a section which
	      causes the variable to be attached to the section instead of remaining global
	    Rename SslOrg -> SslSvc to better reflect what it is
	    readme ...
	    update Docs/Changelog.rst


**[1.8.4] ----- 2023-11-25** ::

	    update project version
	    Add missing deps to PKGBUILD
	    rename dns_tools -> ssl_dns
	    Forgot to add conf.d.examples to git
	    Rename conf.d -> conf.d.examples
	    Better comment in service examples
	    update Docs/Changelog.rst


**[1.8.3] ----- 2023-11-25** ::

	    update project version
	    more readme work
	    edit sslm-mgr help a bit more
	    Add config examples, fix help, more work on readme
	    update Docs/Changelog.rst


**[1.8.2] ----- 2023-11-25** ::

	    update project version
	    put examples under conf.d
	    More readme edits
	    remove sslm-cert-expiry.py
	    remove sslm-cleanup-hook.py
	    Move conf.d to examples/conf.d
	    readme
	    db/next_to_curr - fix service name when writing to info file
	    continue working on readme
	    Restrict file perms on bundle.pem as contains privkey
	    Enhance svc_depends to support both:
	       [domain, [svc...]] as well as [any, [web-ec]] to, for example, reload web server for any web
	       cert change
	    dumb typo (missing not in if)
	    fix args for check_dns_primary in cbot/sign_cert
	    Make dns_primary separate config - array of tables
	    Simplify config groups by using array of tables
	    remove breakpoint
	    Config change - remove active_groups and create new table groups
	    update Docs/Changelog.rst


**[1.8.1] ----- 2023-11-23** ::

	    update project version
	    Edit readme a little
	    update Docs/Changelog.rst


**[1.8.0] ----- 2023-11-23** ::

	    update project version
	    tlsa update: sort the merged set of services to ensure tlsa file is always written in same order. Sets are unordered and weirdly change on repeated runs doing nothing
	    More hatch tidy ups
	    update Docs/Changelog.rst


**[1.7.0] ----- 2023-11-23** ::

	    update project version
	    Switch from poetry to hatch
	    update file copyright to be in SPDX format
	    update Docs/Changelog.rst


**[1.6.0] ----- 2023-11-22** ::

	    update project version
	    tlsa bugfix - make sure to always include all services command line plus config file.
	      Without this, running one command line service would have apex_domain tlsa file only using that service.
	      So instead we read and save all groups, services from config file and merge those with command line
	      to create domain level tlsa file (tlsa_update_domain)
	    Improve log when no curr cert - can be missed roll or new cert
	    New acme account sleep now 2 secs
	    After creating a new letsencrypt account, wait a few seconds before using it
	    fix typoe in cbot sign cert
	    cbot sign - change certbot to log instead of logv certbot arguments
	    duh - added log to server restart but forgot to set log function!
	    Add newline in between each cert info in chain
	    cert_info_print - break up long sans lines.
	    sslm-verify now uses cert_info_print
	    update Docs/Changelog.rst


**[1.5.0] ----- 2023-11-22** ::

	    update project version
	    Add ssl-verify to verify cert using chain public key
	    Clean up sslm-info by putting more support in certs module
	    update Docs/Changelog.rst


**[1.4.0] ----- 2023-11-21** ::

	    update project version
	    Add log when checking for server restarts
	    fix bug in server restarts checking wrong data structure
	    Change opts check to use logs instead of log
	    update Docs/Changelog.rst


**[1.3.0] ----- 2023-11-21** ::

	    update project version
	    config - support skip_prod_copy usefule for dev and if server has NFS access to certs.
	    Fixes in server_restarts for new changes tracker
	    Track changes at fine grain level.
	    Allows us to define dependencies that trigger server restarts when deps changed.
	    2 kinds of deps (service deps and higher level ones like "dns" or "tlsa"
	    Update certs to prod and server restart for new data format
	    Big config reorg and tidy.
	      Preps us for next step handling restarts only when dependencies change.
	      Want to only restart postfix when its certs changed
	                   restart dns server when dns changed (new TLSA records)
	      These restarts are once all tasks have been completed.
	    Fix bug server restart - said failed when succeeded
	    Roll next to curr - when there is no curr, its okay to roll next to curr
	      even if next is below time threshold (90 mins or so).
	      This is the normal situation when first create a cert - its created in next and curr doesnt exist
	    service - nothing to roll is not an error
	    update Docs/Changelog.rst


**[1.2.0] ----- 2023-11-20** ::

	    update project version
	    tweak check_acme. Recognize once NS have domain info
	      They will have all (sub)domain info too - so dont sleep at beginning of domain check
	    Fix dns_tools:: check_acme - handle not finding RR bug
	    Fix dumb bug where class_certbot initialized logger to wrong directory
	      Not writable dir - so failed
	    More work on server_restarts - fixes bug.
	      Try all restarts now, and report number of fails instead of quiting on first fail
	    Acme account registration is now down separately ahead of any cert request.
	       Prior method adding acct reg to certbot in manual mode seems to fail - or there is another bug somewhere.
	       testing will hopefully show if bug fixed or not
	    fix typo in cert_status format string
	    cert_status = handle case when cert missing
	    App server restart - if on same machine run command otherwise ssh remote command.
	       i.e. only ssh if machine is remote
	    fix typo
	    In test mode prod_cert_dir has ".test" appendewd
	    update Docs/Changelog.rst


**[1.1.0] ----- 2023-11-19** ::

	    update project version
	    lint
	    Enhance sslm-dhparm. Now checks file times and only updates
	      when param file is older than 120 days. Can be overriden with -f. Key sizes now default
	      and -k allows user input.  One or more directories on command line have dh/xx param files unless
	      -s (subdir) option which then gets list of subdirs of each command line dir.
	      Good default cron is now:
	          sslm-dhparm -s /etc/ssl-mgr/prod-certs
	    Update cron sample
	    update Docs/Changelog.rst


**[1.0.0] ----- 2023-11-18** ::

	    update project version
	    db: add service name to info file with datetime certs rolled to current
	    Too soon to roll for one service is not an error.
	      Want to allow things to to try other services, other groups
	    Put groups class in its own module
	    mv tlsa to its own module.
	    Rename tlsa_hash to dns_file_hash and move to dns_tools module
	    Tidy up ssl_db.
	    Add optional log to write_path_atomic and copy_file_atomic
	    Disallow remote copy certs to production if directory is not absolute path
	    update Docs/Changelog.rst


**[0.17.0] ----- 2023-11-17** ::

	    update project version
	    Fix certs_to_prod returning fail after success copy to remote
	    certs-changed=false prevented dev option --certs-to-prod working
	    Add missing logv to class_certbot as being used in sign_cert
	    Add write_path_atomic() copy_file_atomic()
	    update Docs/Changelog.rst


**[0.16.0] ----- 2023-11-13** ::

	    update project version
	    Check if root before restarting any servers
	    update Docs/Changelog.rst


**[0.15.0] ----- 2023-11-13** ::

	    update project version
	    org: add check that group and service names match group_dir svc_file
	    Fix typo2
	    typos etc


**[0.14.0] ----- 2023-11-13** ::

	    Add separate check for curr vs next certs changing.
	    Enhance logic of sslm-mgr:
	    - Order is important
	        - certs changed:
	              - push cert/key files to production
	                Will be either curr + next, or just curr - push them all
	              - push cert/keys to all servers (web and all email servers)
	        - new curr (special case of certs changed) (happens when doing roll)
	              - restart all email servers (internal + border)
	                so they get the new curr keys/certs
	              - NB nginx does NOT need restart to pick up cert change
	        - If dns changed (tlsa records) - special case of certs changed
	              - resign zones push to primary
	    Tweak logging
	    First pass at quieter logging
	    logger now has logv() which only logs when verbose
	      And logsv() which logs to file and only logs to stdout when verbose is set
	    dns_restart - use --serial_bump instead of --serial-bump to sign zones
	    sslm-info now defaults to summary and -v provides verbose openssl output
	    update Docs/Changelog.rst


**[0.13.0] ----- 2023-11-12** ::

	    update project version
	    leave challenge_proto to auth_hook to determint
	    cbot:auth_push_http - in debug save web tokens to cb/tokens/xxx
	    class_tasks: add cert_change_requested to help case when
	      next/cert changed due to keyboard interrupt or a problem and user does --status.
	      This should not be pushed out
	    dns_restart: accept domain or [domains]
	    dns_restart: log output of resign zone
	    update Docs/Changelog.rst


**[0.12.2] ----- 2023-11-11** ::

	    update project version
	    Add missing file rdata_format.py
	    update Docs/Changelog.rst


**[0.12.1] ----- 2023-11-11** ::

	    update project version
	    Add org module which was pulled out of certs
	    update Docs/Changelog.rst


**[0.12.0] ----- 2023-11-11** ::

	    update project version
	    dns_tools: now offers dns_tlsa_record_format, dns_txt_record_format.
	      Change acme-challenge for dns to use dns_txt_record_format to format the rdata portion of record
	    variable name change to better represent what it is (tlsa_data)
	    Fix reuse case - reuse key but regenerate CSR.
	    TLSA now supports match-type=0 (no hash) - output is hex encoded DER format.
	    Add dns_tools/dns_txt_record_format to handle long rdata
	        splits it into strings up to 72 chars each
	    org now in its own module.
	    Increase log file size from 10k to 100k.
	    Minimum files to keep when cleaning now set to 1 plus any linked by curr/next.
	    Add min clean_keep check to options checker
	    remove now unused files


**[0.11.0] ----- 2023-11-10** ::

	    Bug fixes.
	    For TLSA using pub key format selector 1 hash is on pub key in DER format.
	        update cert.get_pubkey_hash() to take option for PEM or DER.
	    Updates/fixes for tlsa - was ignoring the selector - now gets correct hashes
	    update Docs/Changelog.rst


**[0.10.0] ----- 2023-11-10** ::

	    update project version
	    Make sure clean keeps at least 2
	      Could be 0 since cleaner keeps N plus any that are referenced by curr/next links
	    renew_expire_days now set in global ssl-mgr config
	      Can be overriden in each service org config
	    Add check for group services having configs
	    update Docs/Changelog.rst


**[0.9.11] ----- 2023-11-10** ::

	    update project version
	    Change service.org config file to service
	    tweak cert info shown
	    Major re-org and simplifications.
	    Remove certbot config and now shares ssl-mgr.config - so all in one place
	    cbot/sign certbot command now only logged to logfile
	    remove clean_all flag from cleanup as already has opts
	    update cleanup code to current directory structure
	    Add warning in time-to-renew if no curr cert
	    Change code to save both curr/next, if found, in prod_cert_dir.
	    Add back test,dry_run from opts into SslCA.
	      Its now option only and removed from CAInfo (ca-info.conf file)
	    fix typo
	    update Docs/Changelog.rst


**[0.9.10] ----- 2023-11-09** ::

	    update project version
	    Add support for info about certs/csr/keys in pem format.
	    sslm-info now uses the internal cert_info tools with "-s" option, otherwise uses openssl standalone
	    tweak format of verbose cert_info
	    update Docs/Changelog.rst


**[0.9.9] ----- 2023-11-08** ::

	    update project version
	    cert info add: signature algo and pubkey algo
	    update Docs/Changelog.rst


**[0.9.8] ----- 2023-11-08** ::

	    update project version
	    Add SslCert.cert_info() to provde expiration, issuer, subject and sans
	    update Docs/Changelog.rst


**[0.9.7] ----- 2023-11-08** ::

	    update project version
	    More fixups with executing tasks
	    Simplify and re-org group level task execution.
	    Now do all tasks for each service - also allows simple way to check cert expirations for renewaal
	        before doing any service level task
	    little buglets from re-org fixed
	    Big code re-org.
	    At group level introduce task class to handle tasks and derived tasks.
	    Remove service level auto generation of keys/csr since hadnled by TaskMgr class now.
	    If service task is not ready its now an error.
	    Handle "dev" requests as well as standard requests.
	    roll_next_to_curr now checks enough time has passed before doing it.
	    (dev next_to_curr) will force the roll regardless of time since next cert till now.
	    Move app tasks from class_mgr to execute_tasks.
	    group.do_tasks() now returns error to caller
	    Add cert_changed checks to drive what to copy / push etc.
	    Fix bug with tlsa_changed code
	    rename push_keys_certs to certs_to_prod
	    rename save_clean to save_keep
	    Separate "dev" options from standard options.
	      dev options available by using "dev" as first argument.
	      Change name "certs_keys_dir" to "prod_certs_dir"
	    debug off
	    more work on tlsa.
	    SslGroup updates the apex_domain tlsa file - and checks for changes
	    SslGroup also copies the tlsa file to dns_tlsa_dirs.
	    SslMgr checks with SslGroup for any changes and if yes, then resign/push dns zones
	    Compute hash of each domains tlsa_file before and after
	      so can sign dns zone files and push when there is a change effecting dns.
	      Only thing impacting dns (aside from acme-challenges) is tlsa files per domain
	    ssl-mgr.conf now has active_groups and their services.
	      Can be overriden on command line.
	    Improve code comments.
	    SslGroup: now calls tlsa_update_domain after any new cert.
	    SslSvc when making new cert now keeps next during roll-1 instead of always moving next-to-curr
	    Fix silly typo in class_service.renew.
	    Fix directory check in certbot.sign_cert was giving false warning
	    renew - make sure next available and has priv key
	    New option --renew-cert-now. Same as --renew-cert but current cert expiration is ignored. i.e. renew is forced on regardless if close to expiration or not
	    class_key - make sure privkey is protected
	    Fixes for state: org changes mean cert out of date
	    state tracking - keys now depends on org file.
	      For example if (sub)domain added to SAN list we regenerate keys.
	      Or if key_opts changes then we regen keys
	    class_service make sure refresh_paths & state.update() used
	    more cleanups
	    Remove dns_includes_dir replae with:
	      dns_acme_dir : certbot.conf includes for dns acme challenge RRs
	      dns_tlsa_dirs : ssl-mgr.conf list of dirs to push files with dns TLSA records
	    New module dns_tools (taken out of utils)
	    Comments sslm-info.py
	    renew/refresh now run next-to-curr
	    Fix error check in push_keys_certs to avoid false fail message
	    Update sslm-cert-expiry app with expiration date string
	    Show expiry date as well as days to expiration
	    Code tidy


**[0.9.6] ----- 2023-11-02** ::

	    fixups for renew
	    First draft of renew_cert refresh_cert
	    cert_time_to_expire now returns days to expiration
	    Add support to check if certificate is expiring.
	    Add app to check certificate application - also tests expiry check code


**[0.9.5] ----- 2023-11-01** ::

	    Significant changes: each cert producer saves cert.pem, chain.pem, fullchain.pem
	     bundle.pem is generated after certificate is generated.
	     certbot has been told where to save certs - i.e. into our db_dir same as signed by our CA.
	     clean up more unused code
	    auth_http : make sure token files are readable by web server
	    put auth http cleanup back on
	    Add newline after the validation text in the http challenge file
	    typo
	    cbot - only check for cerbot env if called by cerbot as manual auth hook.
	    run_prog change logging logic
	    Fix typos
	    Fix path to check if LE account is registered
	    auth_push - more logs
	    Add more output info to sslm-auth-hook
	    debug off
	    More care with absent cert in debug mode.
	    Add logging to auth_hook
	    Code tidy ups for certbot.
	    Remove certbot "renew" cert and rely on checking if acct is registered or not to decide whether any email etc is needed to register.
	    csr_build - code tidy
	    Fixup dhparm_update.sh and cron to match what latest sslm-dhparm.py does which is to take a directory argument, and create dhparams for every directory (domains) in that dir.
	    Pass opts to SslCA class
	    Add logging to SslCA class
	    update Docs/Changelog.rst


**[0.9.0] ----- 2023-10-29** ::

	    update project version
	    csr_build: fix san buglet with [list] instead of list.
	    Fix cert sign expiration to be max(30, days) instead of min(30,days)


**[0.8.0] ----- 2023-10-28** ::

	    Fix up extracting extensions from csr and adding to cert.
	    Fix couple smale buglets with all new crypto code
	    Move all crypto code to cryptography.xxx remove all OpenSSL references.
	      Means we now use one library and the hazmat module.
	      Reorg / tidy certs module
	    code tidy contd
	    Clean ups contd
	    More code cleaning
	    update Docs/Changelog.rst


**[0.7.0] ----- 2023-10-27** ::

	    update project version
	    Dont import pdb unless we debugging
	    sslm-dns-copy-push add import os
	    more code tidy
	    Improve option help
	    bug fix read_mgr after moved into option initializer
	    More code tidy ups
	    Code tidy
	    Tidy up some code
	    Options help tweak
	    Tidy up class_opts
	    fixups for self signed ca which got broken with cbot work
	    debug off
	    update Docs/Changelog.rst


**[0.6.0] ----- 2023-10-26** ::

	    update project version
	    few more cbot fixups - all minor
	    sslm-info : add CSR support
	    class_log: make sure logdir exists
	    Add logger
	    add print to certbot cleanup
	    update Docs/Changelog.rst


**[0.5.0] ----- 2023-10-25** ::

	    update project version
	    Fixup certbot cleanup after (re)new_cert() call
	    Get working version of cleanup_hook - then dont use it
	      certbot.sign_cert() and certbot.renew_cert() now call cleanup directly so we dont
	      use certbots manual-cleanup-hook. And certbot may even call the cleanup hook for
	      every (sub)domain in the cert - whereas we can clean up everything at same time
	    Improve certbot cleanup_hook
	    update Docs/Changelog.rst


**[0.4.0] ----- 2023-10-25** ::

	    update project version
	    Tidy up certbot auth_push
	    More work on certbot paths
	    update Docs/Changelog.rst


**[0.3.0] ----- 2023-10-25** ::

	    update project version
	    rename cerbot to cbot to avoid any possible name conflict
	    update Docs/Changelog.rst


**[0.2.0] ----- 2023-10-25** ::

	    update project version
	    Rename executables sslm-xxx
	    Remove libexec from src directory and put those into /usr/lib/ssl-mgr in installer
	    fix installer libexec bug
	    Code read fixups for certbot
	    Fix links to point to ../ssl_mgr insteadof ssl-mgr
	    Pass opts around more - still missing SslCA case for signing_ca.
	    Clean up some str vs byte things in run_prog and make it more flexible for input string
	    Add more dependencies to PKGBUILD
	    fix libexec install


**[0.1.0] ----- 2023-10-24** ::

	    Initial commit:
	      - self signed create cert tested
	      - letsencrypt completely untested
	      - push functionality (challenges to web server or dns or tlsa to dns) all untested


