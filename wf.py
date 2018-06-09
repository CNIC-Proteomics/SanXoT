import sys
import os
import logging
import re

import aljamia
import klibrate
import sanxot
import sanxotsieve


# Module metadata variables
__author__ = "Jose Rodriguez"
__credits__ = ["Marco Trevisan", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "1.0.1"
__maintainer__ = "Jose Rodriguez"
__email__ = "jmrodriguezc@cnic.es"
__status__ = "Development"

from cStringIO import StringIO
class capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

class builder:
    '''
    Handle SanXoT workflow
    '''
    def __init__(self, outdir, logger=None):
        '''
        Workflow builder
        '''
        # prepare tmp workspace ---
        self.tmpdir = outdir +"/tmp"
        try:
            os.makedirs(self.tmpdir)
        except:
            pass
        # create logger instance for a job
        if logger is not None:
            self.logger = logger
        else:
            # TODO!! improve the logger instance when it is not given by input
            self.logger = logging.getLogger(__name__)        
        
    def _convert_dict_list(self, r, o):
        '''
        Convert the dictionary to list
        '''
        # init with temporal directory
        dlist = []
        if self.tmpdir:
            dlist.append("-p")
            dlist.append(self.tmpdir)
        # join dict with requried and optional parameters        
        params = r.copy()
        if o is not None:
            if type(o) is dict:
                params.update(o)
            elif type(o) is str:
                dlist.extend( o.split() )
        # create parameter list
        for key, value in params.iteritems():
            dlist.append( str(key) )
            if value != "":
                dlist.append( str(value) )
        return dlist

    def _check_params(self, iparams, method):
        '''
        Check the parameters depending on the method
        '''
        # TODO!!!
        return True

    def _print_exception(self, code, msg):
        '''
        Print the code message
        '''
        self.logger.exception(msg)
        sys.exit(code)

    def _get_opt_params(self, core, method, optparams):
        '''
        Get the optional parameters
        '''
        optparam = None        
        if core in optparams and method in optparams[core]:
            optparam = optparams[core][method]
        return optparam

    def aljamia(self, iparams, optparams=None):
        '''
        Preparate the input data
        '''
        params = self._convert_dict_list(iparams, optparams)
        self.logger.debug( "execute aljamia: "+ " ".join(params) )
        try:
            with capturing() as outlog:
                aljamia.main( params )
        except:
            self._print_exception(2, "Exception occured: executing aljamia")

    def klibrate(self, iparams, optparams=None):
        '''
        Calibrate data
        '''
        params = self._convert_dict_list(iparams, optparams)
        self.logger.debug( "execute klibrate: "+ " ".join(params) )
        try:
            with capturing() as outlog:
                klibrate.main( params )
        except:
            self._print_exception(2, "Exception occured: executing klibrate")

    def sanxot(self, iparams, optparams=None):
        '''
        Calibrate data
        '''
        params = self._convert_dict_list(iparams, optparams)
        self.logger.debug( "execute sanxot: "+ " ".join(params) )
        try:
            with capturing() as outlog:
                sanxot.main( params )
        except:
            self._print_exception(2, "Exception occured: executing sanxot")

    def sanxotsieve(self, iparams, optparams=None):
        '''
        Calibrate data
        '''
        params = self._convert_dict_list(iparams, optparams)
        self.logger.debug( "execute sanxotsieve: "+ " ".join(params) )
        try:
            with capturing() as outlog:
                sanxotsieve.main( params )
        except:
            self._print_exception(2, "Exception occured: executing sanxotsieve")


    def scan2peptide(self, iparams, optparams=None):
        '''
        Function scan to peptide
        '''
        corename = "scan2peptide"
        coreabrv = "S2P"

        # execution ---
        method = 'aljamia1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.aljamia({
            "-x": iparams['-x'],
            "-o": "s2p_uncalibrated.xls",
        }, optparam)

        # execution ---
        method = 'aljamia2'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.aljamia({
            "-x": iparams['-x'],
            "-o": iparams['-r'],
        }, optparam)

        # execution ---
        method = 'klibrate1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.klibrate({
            "-d": "s2p_uncalibrated.xls",
            "-r": iparams['-r'],
            "-o": iparams['-d'],
        }, optparam)

        # execution ---
        method = 'sanxot1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxot({
            "-a": "s2p_outs",
            "-d": iparams['-d'],
            "-r": iparams['-r'],
        }, optparam)

        # execution ---
        method = 'sanxotsieve1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxotsieve({
            "-d": iparams['-d'],
            "-r": iparams['-r'],
            "-f": iparams['-f'],
            "-V": "s2p_outs_infoFile.txt",
        }, optparam)

        # execution ---
        method = 'sanxot2'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxot({
            "-a": "s2p_nouts",
            "-d": iparams['-d'],
            "-r": "scans_tagged.xls",
            "-o": iparams['-o'],
            "-V": "s2p_outs_infoFile.txt",
        }, optparam)
        

    def peptide2protein(self, iparams, optparams=None):
        '''
        Function peptide to protein
        '''
        corename = "peptide2protein"
        coreabrv = "P2Q"

        # execution ---
        method = 'aljamia1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.aljamia({
            "-x": iparams['-x'],
            "-o": iparams['-r'],
        }, optparam)

        # execution ---
        method = 'sanxot1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxot({
            "-a": "p2q_outs",
            "-d": iparams['-d'],
            "-r": iparams['-r'],
        }, optparam)

        # execution ---
        method = 'sanxotsieve1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxotsieve({
            "-d": iparams['-d'],
            "-r": iparams['-r'],
            "-f": iparams['-f'],
            "-V": "p2q_outs_infoFile.txt",
        }, optparam)

        # execution ---
        method = 'sanxot2'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxot({
            "-a": "p2q_nouts",
            "-d": iparams['-d'],
            "-r": "peptides_tagged.xls",
            "-o": iparams['-o'],
            "-V": "p2q_outs_infoFile.txt",
        }, optparam)


    def peptide2category(self):
        '''
        Function peptide to category
        '''
        print("peptide to category")


    def protein2category(self, iparams, optparams=None):
        '''
        Function protein to category
        '''
        corename = "protein2category"
        coreabrv = "Q2C"

        # execution ---
        method = 'sanxot1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxot({
            "-a": "q2c_outs",
            "-d": iparams['-d'],
            "-r": iparams['-r'],
        }, optparam)

        # execution ---
        method = 'sanxotsieve1'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxotsieve({
            "-d": iparams['-d'],
            "-r": iparams['-r'],
            "-f": iparams['-f'],
            "-V": "q2c_outs_infoFile.txt",
        }, optparam)

        # execution ---
        method = 'sanxot2'
        self.logger.info(coreabrv+": execute "+method)
        optparam = self._get_opt_params(corename, method, optparams)
        self.sanxot({
            "-a": "q2c_nouts",
            "-d": iparams['-d'],
            "-r": "proteins_tagged.xls",
            "-o": iparams['-o'],
            "-V": "q2c_outs_infoFile.txt",
        }, optparam)


    def peptide2all(self):
        '''
        Function peptide to all
        '''
        print("peptide to all")

    def protein2all(self):
        '''
        Function protein to all
        '''
        print("protein to all")

    def protein2all(self):
        '''
        Function category to all
        '''
        print("category to all")
