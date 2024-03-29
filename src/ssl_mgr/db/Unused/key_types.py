#!/usr/bin/python
"""
Coordinate which key types with certs library
This could be in certs, but that leads to circular imports
"""

def get_key_types() -> [str]:
    """
    return tuple of supported key types
    """
    ktypes = ('rsa', 'ec')
    return ktypes
