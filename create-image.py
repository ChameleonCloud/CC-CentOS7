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
import sys

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-r', '--revision', type=str,
        help='Revision to build with, usually of the format YYMM', required=True)
    parser.add_argument('-v', '--variant', type=str,
        help='Image variant to build.') # extra elements defined in the .sh
    parser.add_argument('-c', '--cuda-version', type=str, default='cuda9',
        help='CUDA version to install. Ignore if the variant is not gpu.')
    parser.add_argument('-g', '--region', type=str, required=True, help='Region name (for FPGA)')
    

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
        os.execl('create-image.sh', 'create-image.sh', '--variant', args.variant, '--cuda', args.cuda_version)
    else:
        os.execl('create-image.sh', 'create-image.sh', '--variant', args.variant, '--region', args.region)

if __name__ == '__main__':
    sys.exit(main())
