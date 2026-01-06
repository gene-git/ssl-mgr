# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
'''
Generate list of services in a directory
 - used when services config set to "*"
'''
import os
import re

from ssl_mgr.utils import (dir_list, open_file)


def read_file(file: str) -> list[str]:
    '''
    Read and return rows
    '''
    fob = open_file(file, 'r')
    data: list[str] = []
    if fob:
        data = fob.readlines()
        fob.close()
    return data


def is_wildcard_services(services: str | list[str]) -> bool:
    '''
    Check if wild card (* or ALL)
    '''
    if not services:
        return False

    if isinstance(services, list):
        for item in services:
            if item in ('*', 'ALL'):
                return True
    elif services in ('*', 'ALL'):
        return True
    return False


def check_is_service(group: str, file: str) -> bool:
    '''
    Check file is a service config
    '''
    checks = ['name=', 'group=', 'service=', '[KeyOpts]', '[X509]']
    checks_todo = list(checks)
    found = {}
    num_checks = len(checks)

    for check in checks:
        found[check] = False

    path = os.path.join(group, file)
    rows = read_file(path)

    num_checks_found = 0
    is_service_config = False
    for row in rows:
        # strip all white space
        row = re.sub(r"\s+", '', row)
        if row == '' or row.startswith('#'):
            continue

        checks = list(checks_todo)
        for check in checks:
            if not found[check] and row.startswith(check):
                found[check] = True
                num_checks_found += 1
                checks_todo.remove(check)
                break

        if num_checks_found == num_checks:
            is_service_config = True
            break

    return is_service_config


def service_list_from_dir(conf_dir: str, group: str) -> list[str]:
    '''
    Generate list of service configs located in conf_dir/group_dir
    '''
    group_dir = os.path.join(conf_dir, group)
    (files, _dirs, _links) = dir_list(group_dir)
    if not files:
        return []

    # checks that file is a service config
    service_files = []
    for file in files:
        if check_is_service(group_dir, file):
            service_files.append(file)

    return service_files
