# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
CSR tools
"""
from cryptography.x509 import load_pem_x509_csr
from utils import read_pem
from utils import write_pem

def read_csr(csr_dir:str, csr_file:str) :
    """
    Read csr from file in PEM format
    return (csr, csr_pem)
    """
    csr_pem = read_pem(csr_dir, csr_file)
    csr = None
    if csr_pem:
        csr = load_pem_x509_csr(csr_pem)

    return (csr, csr_pem)

def write_csr(csr_pem:bytes, csr_dir:str, csr_file:str):
    """
    Save csr pem to file
    """
    is_okay = write_pem(csr_pem, csr_dir, csr_file)
    return is_okay
