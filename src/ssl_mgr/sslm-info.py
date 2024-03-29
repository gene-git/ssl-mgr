#!/usr/bin/python
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Managerment Tools

 - Display Info about keys and certs (in pem format)
 - Default mode uses internal code 
 - With "-v" invokes "openssl" to give independent view.
"""
# pylint: disable=invalid-name
import sys
from utils import open_file
from utils import run_prog
from certs import csr_pem_info, cert_pem_info, key_pem_info
from certs import cert_info_print, cert_split_pem_string

def _help():
    """
    usage
    """
    me = sys.argv[0]
    print(f'{me} [-s] [-h] [pem file(s)]')
    print('  Disply information about cert, key, chain or csr file(s) in pem format')
    print('  Pem files read from stdin if not specified')
    print('  By default uses internal code to display summary ')
    print('  -v :  provide more verbose details calling openssl')

def _options():
    """
    If "-s" then summary => True
    All remaining args are passed back
    in argv (or None)
    Returns
      (summary, argv)
    """
    summary = True
    argv = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            _help()
            sys.exit()

        argv = sys.argv[1:]
        if sys.argv[1] in ('-v', '--verb', '--verbose'):
            summary = False
            if len(sys.argv) > 2:
                argv = sys.argv[2:]

    return (summary, argv)

def _read_cert(argv):
    """
    Read into buffer
    """
    data = {}
    if argv :
        for file in argv:
            fobj = open_file(file, 'r')
            if fobj:
                #buf = fobj.readlines()
                buf = fobj.read()
                data[file] = buf
                fobj.close()
            else:
                print(f'Error reading {file}')
    else:
        fobj = sys.stdin
        #buf = fobj.readlines()
        buf = fobj.read()
        data['stdin'] = buf

    return data

def _show_one(label:str, pem_string:str):
    """
    Print content of one item
    Can handle:
      Certificate       : 'cert' 
      Key (EC or RSA)   : 'key'
      CSR               : 'req'
    """
    if 'KEY' in label:
        ssl_cmd = 'ec'

    elif 'REQUEST' in label:
        ssl_cmd = 'req'
    else:
        ssl_cmd = 'x509'

    pargs = ['/usr/bin/openssl', ssl_cmd, '-text', '-noout']
    [retc, out, err] = run_prog(pargs, input_str=pem_string)
    if retc != 0:
        print(f'Error : {retc}')
        print(err)
    elif out:
        print(out)

def _show_summary(label:str, pem_string:str):
    """
    Use internal library to parse the certificate
    """
    pem_bytes = pem_string.encode()
    if 'KEY' in label:
        info = key_pem_info(pem_bytes)
        print(info)

    elif 'REQUEST' in label:
        info = csr_pem_info(pem_bytes)
        cert_info_print(info)

    else:
        info = cert_pem_info(pem_bytes)
        cert_info_print(info)


def _process_all(summary, data):
    """
    Process each item in data.
      Each item may need to be split into individuaal parts
    """
    if not data:
        return

    for (_file, buf) in data.items():
        pem_items = cert_split_pem_string(buf)

        if not pem_items:
            continue

        for (label, cert_pem) in pem_items:
            if summary:
                _show_summary(label, cert_pem)
            else:
                _show_one(label, cert_pem)

def main():
    """
    Certificate manager
    """
    (summary, argv) = _options()
    data = _read_cert(argv)
    _process_all(summary, data)

# -----------------------------------------------------
if __name__ == '__main__':
    main()
# -------------------- All Done ------------------------
