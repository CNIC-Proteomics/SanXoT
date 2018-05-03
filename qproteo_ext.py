#!/usr/bin/python

# import global modules
import os
import sys
import argparse
import logging
import json
import pandas
import Queue
import multiprocessing
import signal


import time


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

# Global variables
NUM_CPUs = multiprocessing.cpu_count() * 0.67 # 2/3 of the all CPUS
signal.signal(signal.SIGINT, signal.SIG_IGN)


def qproteo(indata):
    '''
    Function that calls the functions in the qProteo workflow
    '''
    
    # TODO!! check input parameters

    # extract input data
    idqfile    = indata["idqfile"]
    experiment = indata["experiment"]
    tag        = indata["tag"]
    controltag = indata["controltag"]
    fdr        = indata["fdr"]
    outdir     = indata["outdir"] +"/"+ experiment +"/"+ tag
    workname   = experiment +"_"+ tag
    if "scanfile" in indata:
        scanfile = outdir +"/"+ indata["scanfile"]
    else:
        scanfile = outdir +"/scans.xls"
    if "pepfile" in indata:
        pepfile = outdir +"/"+ indata["pepfile"]
    else:
        pepfile = outdir +"/peptides.xls"
    if "profile" in indata:
        profile = outdir +"/"+ indata["profile"]
    else:
        profile = outdir +"/proteins.xls"
    if "catfile" in indata:
        catfile = outdir +"/"+ indata["catfile"]
    else:
        catfile = outdir +"/categories.xls"
    logfile = outdir + "/qproteo.log"

    # start the execution of job
    logging.info("executing job: "+workname)

    # prepare workspace ---
    try:
        os.makedirs(outdir)
    except:
        pass
  
    # create logger ---
    logger = create_logger(logfile, workname)

    # create builder ---
    logger.info("create workflow builder")
    w = wf.builder(outdir, logger)

    # SCAN TO PEPTIDE -----------------------------------
    logger.info("aljamia for scan uncalibrated")
    w.aljamia({
        "-x": idqfile,
        "-o": "s2p_uncalibrated.xls",
        "-i": "[Raw_FirstScan]-[Charge]",
        "-j": "[Xs_"+ tag +"_"+ controltag +"]",
        "-k": "[Vs_"+ tag +"_"+ controltag +"]",
        "-f": "[Modified]==TRUE",
        "-l": "PTM",
        "-R": "1"
    })

    logger.info("aljamia for s2p relationship")
    w.aljamia({
        "-x": idqfile,
        "-o": "s2p_rels.xls",
        "-i": "[Sequence]",
        "-j": "[Raw_FirstScan]-[Charge]",
        "-k": "PTM",
        "-f": "[Modified]==TRUE",
        "-R": "1"
    })

    logger.info("klibrate scans")
    w.klibrate({
        "-d": "s2p_uncalibrated.xls",
        "-r": "s2p_rels.xls",
        "-o": scanfile,
        "-g": "",
        "-f": ""
    })
    
    logger.info("execute sanxot")
    w.sanxot({
        "-a": "s2p_outs",
        "-d": scanfile,
        "-r": "s2p_rels.xls",
        "-g": "",
        "-b": "",
        "-s": ""
    })

    logger.info("execute sanxotsieve")
    w.sanxotsieve({
        "-d": scanfile,
        "-r": "s2p_rels.xls",
        "-f": fdr,
        "-V": "s2p_outs_infoFile.txt"
    })

    logger.info("execute sanxot")
    w.sanxot({
        "-a": "s2p_nouts",
        "-d": scanfile,
        "-r": "scans_tagged.xls",
        "-o": pepfile,
        "-V": "s2p_outs_infoFile.txt",
        "--tags": "!out",
        "-f": "",
        "-g": ""
    })

    # PEPTIDE TO PROTEIN -----------------------------------    
    logger.info("aljamia for peptide to protein")
    w.aljamia({
        "-x": idqfile,
        "-o": "p2q_rels.xls",
        "-i": "[FASTAProteinDescription]",
        "-j": "[Sequence]",
        "-k": "PTM",
        "-f": "[Modified]==TRUE",
        "-R": "1"
    })

    logger.info("execute sanxot")
    w.sanxot({
        "-a": "p2q_outs",
        "-d": pepfile,
        "-r": "p2q_rels.xls",
        "-g": "",
        "-b": "",
        "-s": ""
    })

    logger.info("execute sanxotsieve")
    w.sanxotsieve({
        "-d": pepfile,
        "-r": "p2q_rels.xls",
        "-f": fdr,
        "-V": "p2q_outs_infoFile.txt"
    })

    logger.info("execute sanxot")
    w.sanxot({
        "-a": "p2q_nouts",
        "-d": pepfile,
        "-r": "peptides_tagged.xls",
        "-o": profile,
        "-V": "p2q_outs_infoFile.txt",
        "--tags": "!out",
        "-f": "",
        "-g": ""
    })

    # PROTEIN TO CATEGORY -----------------------------------
    logger.info("execute sanxot")
    w.sanxot({
        "-a": "q2c_outs",
        "-d": profile,
        "-r": "q2c_rels.xls",
        "-g": "",
        "-b": "",
        "-s": ""
    })

    logger.info("execute sanxotsieve")
    w.sanxotsieve({
        "-d": profile,
        "-r": "q2c_rels.xls",
        "-f": fdr,
        "-V": "q2c_outs_infoFile.txt"
    })

    logger.info("execute sanxot")
    w.sanxot({
        "-a": "q2c_nouts",
        "-d": profile,
        "-r": "categories_tagged.xls",
        "-o": catfile,
        "-V": "q2c_outs_infoFile.txt",
        "--tags": "!out",
        "-f": "",
        "-g": ""
    })

    # PEPTIDE TO ALL -----------------------------------
    logger.info("execute sanxot")
    w.sanxot({
        "-a": "p2a",
        "-d": pepfile,
        "-C": "",
        "-g": ""
    })

    # PROTEIN TO ALL -----------------------------------
    logger.info("execute sanxot")
    w.sanxot({
        "-a": "q2a",
        "-d": profile,
        "-V": "q2c_outs_infoFile.txt",
        "-f": "",
        "-C": "",
        "-g": ""
    })

    # CATEGORY TO ALL -----------------------------------
    logger.info("execute sanxot")
    w.sanxot({
        "-a": "c2a",
        "-d": catfile,
        "-V": "0",
        "-f": "",
        "-C": "",
        "-g": ""
    })


def create_logger(logfile, workname):
    '''
    Create logger for the multiprocesses
    '''   
    # create logging instance
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.DEBUG)
    
    # formtat
    fmt = '%(asctime)s - %(levelname)s - '+ workname +': %(message)s'
    datefmt = '%m/%d/%Y %I:%M:%S %p'
    formatter = logging.Formatter(fmt, datefmt)

    # add stdout handler
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(formatter)
    logger.addHandler(stdout)

    # add file handler
    fh = logging.FileHandler(logfile) 
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

def worker(q):
    '''
    This is the worker cup function. It processes items in the queue one after another.
    These daemon cups go into an infinite loop, and only exit when the main cup ends.
    '''    
    while not q.empty():
        try:
            # extract input data
            data = q.get()
            # execute workflow
            qproteo(data)
        except Queue.Empty:
            pass
        except KeyboardInterrupt:
            logging.error("parent received ctrl-c")
            pass

def setup_multiprocessing(num_cpus, queue):
    '''
    Set up some cups to fetch the enclosures
    '''
    workers = []
    for i in range(0, num_cpus):
        logging.info("starting process-"+str(i+1))
        proc = multiprocessing.Process( target=worker, args=(queue,) )
        proc.start()
        workers.append(proc)
    return workers
        

def main(args):
    '''
    Main function
    '''
    # Multiprocessing queue
    queue = multiprocessing.Queue()
    
    # extract config data
    logging.info("extract input data")
    if os.path.exists(args.indata):        
        # indata = json.load( open(args.indata) )
        indata = pandas.read_excel(args.indata, na_values=['NA'])
        indata = indata.applymap(str)
    else:
        logging.exception("Exception occured: input data file has not been included")

    # execute processes
    logging.info("execute processes")
    # for indat in indata:
    for idx, indat in indata.iterrows():
        # put the input data to execute the job into the queue
        queue.put( indat )

    # Set up some cpus to fetch the enclosures
    logging.info("set up some cups to fetch the enclosures")
    num_cpus = NUM_CPUs
    if args.ncpus and args.ncpus <= NUM_CPUs:
        num_cpus = args.ncpus
    workers = setup_multiprocessing(num_cpus, queue)
    
    # check if jobs has finished
    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        logging.error("parent received ctrl-c")
        for worker in workers:
            worker.terminate()
            worker.join()


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(
        description='SanXoT workflow',
        epilog='''
        Example:
            qproteo.py -i test/test1-in.json 
        ''')
    parser.add_argument('-i',  '--indata',  required=True, help='Input data in JSON format')
    parser.add_argument('-n',  '--ncpus',   type=int, help='Number of cups')
    parser.add_argument('-v', dest='verbose', action='store_true', help="Increase output verbosity")
    args = parser.parse_args()

    # logging debug level. By default, info level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')

    logging.info('start '+os.path.basename(__file__))
    main(args)
    logging.info('end '+os.path.basename(__file__))

