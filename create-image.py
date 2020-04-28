#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import io
import operator
import os
import re
import requests
import sys

PATH = 'https://cloud.centos.org/centos/7/images/'
INDEX = PATH + 'image-index'

def image_index():
    index = requests.get(INDEX)
    data = {}
    current_section = None
    current_dict = {}
    for line in index.content.split('\n'):
        if re.match('^\[.*\]$', line):
            if 'arch' in current_dict and current_dict['arch'] == 'x86_64':
                data[current_section] = current_dict
                data[current_section]['url'] = PATH + data[current_section]['file']
            current_section = line.replace('[', '').replace(']', '')
            current_dict = {}
        else:
            key_val = line.split('=')
            if len(key_val) == 2:
                current_dict[key_val[0]] = key_val[1]
    return data

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-r', '--revision', type=str,
        help='Revision to build with, usually of the format YYMM', required=True)
    parser.add_argument('-v', '--variant', type=str,
        help='Image variant to build.') # extra elements defined in the .sh
    parser.add_argument('-c', '--cuda-version', type=str, default='cuda10',
        help='CUDA version to install. Ignore if the variant is not gpu.')
    parser.add_argument('-g', '--region', type=str, required=True, help='Region name (for FPGA)')
    parser.add_argument('-k', '--kvm', action='store_true', help='Present if build image for KVM site') 

    args = parser.parse_args()

    try:
        image = next(i for i in image_index().values() if i['revision'] == args.revision)
    except StopIteration:
        print("No image found for revision '{}'".format(args.revision))
        return 1

    # os.environ['IMAGE_URL'] = image['url']
    os.environ['BASE_IMAGE_XZ'] = image['file']
    os.environ['IMAGE_REVISION'] = image['revision']
    os.environ['IMAGE_SHA512'] = image['checksum']
    os.environ['BASE_IMAGE'] = image['file'][:-3]

    if args.variant == 'gpu':
        os.execl('create-image.sh', 'create-image.sh', '--variant', args.variant, '--cuda', args.cuda_version, '--kvm', str(args.kvm).lower())
    else:
        os.execl('create-image.sh', 'create-image.sh', '--variant', args.variant, '--region', args.region, '--kvm', str(args.kvm).lower())

if __name__ == '__main__':
    sys.exit(main())
