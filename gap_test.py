#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""initialize and run the testfarm of GAP2 code for many-body perturbation calculation
"""
from __future__ import print_function, with_statement
import glob
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from utils import create_logger, TestCase

__project__ = "gap2-testcases"
__version__ = "0.0.2"

def gap_parser():
    """parser of gap test"""
    p = ArgumentParser(description=__doc__,
                       formatter_class=RawDescriptionHelpFormatter)
    p.add_argument("--init", action="store_true",
                   help="initialize WIEN2k and GAP inputs")
    filters = p.add_mutually_exclusive_group()
    filters.add_argument("--filter", type=int, default=None, nargs="+",
                         help="testcases to filter out")
    filters.add_argument("--choose", type=int, default=None, nargs="+", help="testcases to run")
    p.add_argument("-n", type=int, dest="nprocs", default=1, help="number of processors")
    p.add_argument("--init-gap", dest="init_gap", action="store_true",
                   help="only initialize GAP inputs with finished WIEN2k SCF")
    p.add_argument("--dry", action="store_true", help="dry run for test use")
    p.add_argument("--gap", dest="gap_version", type=str, default="2c", help="gap version")
    p.add_argument("-d", dest="workspace", type=str, default="workspace", help="working directory")
    p.add_argument("--debug", dest="debug", action="store_true", help="debug mode")
    p.add_argument("--force", dest="force_restart", action="store_true",
                   help="forcing restart an existing testcase")
    return p

def gap_test():
    """run initializtion"""
    args = gap_parser().parse_args()
    logger = create_logger(debug=args.debug)
    init_mode = args.init or args.init_gap
    testcases = list(glob.glob("init/*.json"))
    filters = args.filter
    if filters is None:
        filters = []
    logger.info("Filtering tests: %r", filters)
    choices = args.choose
    if choices is None:
        logger.info("Selected all tests")
        choices = [int(os.path.splitext(os.path.basename(x))[0]) for x in testcases]
    else:
        logger.info("Selected tests: %r", choices)

    for x in testcases:
        logger.info("Found test: %s", x)
        index = int(os.path.splitext(os.path.basename(x))[0])
        if index in filters or index not in choices:
            logger.info("> filtered.")
            continue
        tc = TestCase(x, logger, init_w2k=args.init, workspace=args.workspace,
                      init_gap=init_mode, force_restart=args.force_restart)
        if init_mode:
            tc.init(args.gap_version, dry=args.dry)
        else:
            try:
                tc.run(args.gap_version, nprocs=args.nprocs, dry=args.dry)
            except IOError:
                logger.warning("Test case %s (%s) has been run before hand. Skip.",
                               tc.casename, x)

if __name__ == "__main__":
    gap_test()

