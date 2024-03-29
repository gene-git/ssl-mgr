# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Push curr keys/certs to designated directory
"""
# pylint: disable=duplicate-code
import os
from utils import make_dir_path
from utils import run_prog

def service_to_production(svc:"SslSvc", prod_svc_dir):
    """
    Keys/certs are copied to prod_svc_dir
     - saved to: <svc_dir>/<service>/xxx.pem
     - we copy curr and next but only curr is used of course.
       duing roll we advertise curr/next in tlsa so doesn't hurt to copy
       both. After the roll - then prod curr will be updated and next is 
       left and is actually then identical to the new curr
       If dont want this just copy 'curr'.
    """
    opts = svc.opts
    if not os.path.exists(prod_svc_dir):
        isok = make_dir_path(prod_svc_dir)
        if not isok:
            return False

    logs = svc.logs

    logs(f'{svc.svc_name} :')

    for lname in svc.db.link_names:
        db_name = svc.db.db_names[lname]

        if not db_name:
            continue
        db_dir = os.path.join(svc.db.db_dir, db_name)

        #
        # copy contents to production
        #
        src = os.path.abspath(db_dir)
        src = f'{src}/'

        dst = os.path.join(prod_svc_dir, lname)
        dst = os.path.abspath(dst)
        dst = f'{dst}/'

        pargs = ['/usr/bin/rsync', '-a', '--mkpath', src, dst]

        if opts.debug:
            logs(f'  {pargs}')
        else:
            logs(f'  {lname} {db_name}')
            [ret, _out, _err] = run_prog(pargs, log=svc.log)
            if ret != 0:
                return False
    return True
