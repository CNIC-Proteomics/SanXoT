#!/usr/bin/python

# import global modules
import os
import sys
import argparse
import logging
import re

# import workflow builder
import wf

# Module metadata variables
__author__ = "Jose Rodriguez"
__credits__ = ["Marco Trevisan", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "1.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "jmrodriguezc@cnic.es"
__status__ = "Development"

def _print_exception(code, msg):
    '''
    Print the code message
    '''
    logging.exception(msg)
    sys.exit(code)

def main(args):
    '''
    Main function
    '''
    # check parameters
    # extract params for the methods
    params = {}
    methods = ["sanxot1"]
    for method in methods:
        if not method in args.params:
            _print_exception( 2, "checking the parameters for the {} method".format(method) )
        match = re.search(r'{\s*' + method + r'\s*:\s*([^\}]*)}', args.params, re.IGNORECASE)
        if match.group():
            params[method] = match.group(1)
        else:
            _print_exception( 2, "checking the parameters for the {} method".format(method) )

    # get directory from input files
    outdir = os.path.dirname(os.path.realpath(args.catfile))

    # create builder ---
    logging.info("create workflow builder")
    w = wf.builder(outdir, logging)

    logging.info("execute sanxot")
    w.sanxot({
        "-a": "q2a_outs",
        "-d": args.catfile,
    }, params["sanxot1"])

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(
        description='Create the relationship table for peptide2protein method',
        epilog='''
        Example:
            protein2all.py -i 
            -r 
            -s 
        Parameter example:
            "{aljamia1: -i [Raw_FirstScan]-[Charge] -j [Xs_127_N_126] -k [Vs_127_N_126] -f !([FASTAProteinDescription]~~TRYP_PIG||[FASTAProteinDescription]~~Krt||[FASTAProteinDescription]~~KRT) }
            {aljamia2: -i [Sequence] -j [Raw_FirstScan]-[Charge] }
            {klibrate1: -g  -f }"
        ''')
    parser.add_argument('-c',  '--catfile',  required=True, help='Input file with the categories')
    parser.add_argument('-a',  '--params',  required=True, help='Input parameters for the sub-methods')
    parser.add_argument('-l',  '--logfile',  help='Output file with the log tracks')
    parser.add_argument('-v', dest='verbose', action='store_true', help="Increase output verbosity")
    args = parser.parse_args()

    # set-up logging
    scriptname = os.path.splitext( os.path.basename(__file__) )[0]

    # add filehandler
    logfile = os.path.basename(args.catfile) + "/"+ scriptname +".log"
    if args.logfile:
        logfile = args.logfile

    # logging debug level. By default, info level
    if args.verbose:
        logging.basicConfig(filename=logfile, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - '+scriptname+' - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(filename=logfile, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - '+scriptname+' - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')

    # start main function
    logging.info('start script: '+"{0}".format(" ".join([x for x in sys.argv])))
    main(args)
    logging.info('end script')