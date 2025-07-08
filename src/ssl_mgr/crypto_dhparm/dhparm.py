# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Generate diffie helman param file
"""
import os
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import ParameterFormat
from utils import (open_file, run_prog)


def generate_dh_params(key_size: int):
    """
    Create diffie hellman paramaters
    "generator is 2 or 5" (unlcear what 2 or 5 or if other numbers supported
    """
    gen_type = 2
    dh_parms = dh.generate_parameters(gen_type, key_size=key_size)
    dhparms_pem = dh_parms.parameter_bytes(Encoding.PEM, ParameterFormat.PKCS3)
    return dhparms_pem


def new_dh_params_file(key_size: int, dirpath: str):
    """
    Generate and save to file
    """
    fname = f'dh{key_size}.pem'
    fpath = os.path.join(dirpath, fname)
    dhparms_pem = generate_dh_params(key_size)
    fobj = open_file(fpath, 'wb')
    if fobj:
        fobj.write(dhparms_pem)
        fobj.close()


def _get_named_dh_params(name: str) -> str:
    """
    run openssl to get named pre-defined DH params (PEM)
    """
    pargs = ['/usr/bin/openssl', 'genpkey', '-genparam', '-outform', 'PEM']
    pargs += ['-algorithm', 'DH']
    pargs += ['-pkeyopt', f'dh_param:{name}']
    (retc, dh_params, err) = run_prog(pargs)
    if retc != 0:
        print(err)
        return ''
    return dh_params


def named_dh_params_file(name: str, dirpath: str):
    """
    Generate one of DH named pre-defined files (RFC-7919)
     - at moment cryptography doesn provide access so we call
       openssl to do the work.
    """
    fname = f'dh-{name}.pem'
    fpath = os.path.join(dirpath, fname)
    dhparms_pem = _get_named_dh_params(name)
    if not dhparms_pem:
        return
    fobj = open_file(fpath, 'w')
    if fobj:
        fobj.write(dhparms_pem)
        fobj.close()
