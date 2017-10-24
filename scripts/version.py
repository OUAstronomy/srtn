#!/usr/bin/env python3
'''
File for verifying version control of file versions and python version
'''

# Handling Package Version
def package_version():
    return "0.2"

def python_version():
    from sys import version_info
    return version_info[0]
