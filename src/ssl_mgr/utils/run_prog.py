# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
wg-tool support utils`
"""
# pylint: disable=C0103
import subprocess

def run_prog(pargs,input_str=None,stdout=subprocess.PIPE,stderr=subprocess.PIPE, log=None):
    """
    run external program using subprocess
    """
    if not pargs:
        return [0, None, None]

    bstring = None
    if isinstance(input_str, str):
        #bstring = bytearray(input_str,'utf-8')
        bstring = input_str.encode()

    ret = subprocess.run(pargs, input=bstring, stdout=stdout, stderr=stderr, check=False)
    retc = ret.returncode

    output = ret.stdout
    if isinstance(output, bytes):
        output = output.decode()

    errors = ret.stderr
    if isinstance(errors, bytes):
        errors = errors.decode()

    if log:
        if retc != 0:
            log(f'run_prog exit {retc}')
        if output :
            log(output)
        if errors :
            log(errors)

    return [retc, output, errors]
