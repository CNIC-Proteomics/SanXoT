#!/usr/bin/python

# import global modules
import os
import sys
import argparse
import logging
import pandas
import re

import pprint

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

class corrector:
    '''
    Make the calculations in the workflow
    '''
    def __init__(self, infile, species=None, pretxt=None, indb=None):
        # create species filter
        self.species = species
        # create preferenced text
        self.pretxt = pretxt
        # create an index from the fasta sequence, if apply
        self.indb = None        
        if indb is not None:
            # get the index of proteins: for UniProt case!! (key_function)
            self.indb = SeqIO.index(indb, "fasta", key_function=lambda rec : rec.split("|")[1])
        # create the report with the peptides and proteins
        [self.peptides, self.proteins] = self.get_reports( pandas.read_csv(infile, names=["LPP", "FASTAProteinDescription", "Sequence", "Redundances", "Tags"], header=0, sep="\t", na_values=['NA'], low_memory=False) )
        # logging.info( pprint.pformat(self.peptides) )
        # logging.info( pprint.pformat(self.proteins) )
        # header for the output
        self.rst_header = ['[FASTAProteinDescription]', '[Sequence]', '[Tags]']

    def _extract_proteins_species(self,descs):
        '''
        Extract the protein IDs from a list of FASTA descriptions (for the moment, only applied for UniProtKB)
        Extract the species names from a list of FASTA descriptions (for the moment, only applied for UniProtKB)        
        '''        
        prot_ids = {}
        species = []        
        for desc in descs:
            # discard NaN values
            if pandas.notna(desc):
                for d in desc.split(">")[1:]:
                    # SwissProt/TrEMBL descriptions
                    if re.search(r'^[sp|tr]', d):
                        # extract proteins
                        p_id = d.split("|")[1]
                        if p_id not in prot_ids:
                            prot_ids[p_id] = { 'id': p_id, 'dsc': ">"+d, 'scans': 1}
                        else:
                            prot_ids[p_id]['scans'] += 1
                        # extract species
                        sp = re.search(r'OS=(\w* \w*)', d, re.I | re.M)
                        if sp:
                            sp = sp.group(1)
                            if sp not in species:
                                species.append( sp )
        return [prot_ids, species]
        
    def get_reports(self, df):
        '''
        Create the report with the protein values
        '''
        peptides = {}
        proteins = {}
        # extract the peptide and proteins info for each line
        for row in df.itertuples():
            if ( isinstance(row.Sequence, str) and isinstance(row.FASTAProteinDescription, str) and isinstance(row.Redundances, str) ):
                pep_lpp = row.LPP
                pep_seq = row.Sequence.replace(" ", "")
                pep_p_dsc = []
                pep_p_dsc.append(row.FASTAProteinDescription)
                pep_p_dsc.append(row.Redundances)
                # extract the protein ids from a peptide
                # extract the species from a peptide
                [pep_prots,pep_species] = self._extract_proteins_species(pep_p_dsc)
                peptides[pep_seq] = {
                    'proteins': pep_prots,
                    'species':  pep_species
                    }
                # save the proteins from peptide.
                # the peptide should be unique
                for pid, pep_prot in pep_prots.items():
                    # pid = pep_prot['id']
                    pdsc = pep_prot['dsc']
                    if pid not in proteins:
                        # init LPQ with the first LPP
                        # with the first peptide
                        proteins[pid] = { 'LPQ': pep_lpp, 'desc': pdsc, 'pep': {pep_seq: 1} }
                    else:
                        # check if the peptide is unique
                        # LPQ: Sum of LPP's peptides
                        if pep_seq not in proteins[pid]['pep']:
                            proteins[pid]['pep'][pep_seq] = 1
                            proteins[pid]['LPQ'] += pep_lpp
                        else:
                            proteins[pid]['pep'][pep_seq] += 1
        return [peptides, proteins]

    def _unique_protein_decision(self, prots):
        '''
        Take an unique protein based on
        '''
        decision = False
        hprot = None
        # 1. the preferenced text, if apply
        if self.pretxt is not None:
            # know how many proteins match to the list of regexp
            for pretxt in self.pretxt:
                pmat = list( filter( lambda x: re.match(r'.*'+pretxt+'.*', x['dsc'], re.I | re.M), prots) )
                # keep the matches                
                if pmat is not None and len(pmat) > 0 :
                    prots = pmat
                    # if there is only one protein, we found
                    if len(pmat) == 1:
                        hprot = pmat[0]
                        decision = True
        
        # 2. Take the sorted sequence, if apply
        if (not decision) and (self.indb is not None):
            # extract the proteins that are in the fasta index
            pmat = list( filter( lambda x: x['id'] in self.indb, prots) )
            # extract the sequence length
            pmat = list( map( lambda x: {'id': x['id'], 'dsc': x['dsc'], 'len': len(self.indb[x['id']].seq)}, pmat) )
            # sort by length
            pmat.sort(key=lambda x: x['len'])
            # extract the sorted sequence, if it is unique
            if pmat is not None:
                if len(pmat) == 1:
                    hprot = pmat[0]
                    decision = True
                elif len(pmat) > 1 and pmat[0]['len'] < pmat[1]['len']:
                    hprot = pmat[0]
                    decision = True                
        
        # 3. Alphabetic order
        if not decision:
            # sort the proteins
            pmat = sorted(prots, key=lambda x: x['dsc'], reverse=True)
            if pmat is not None:
                hprot = pmat[0]
                decision = True
        
        return hprot

    def _unique_protein(self, pep_prots):
        scores = {}
        rst = []
        for pid,pep_prot in pep_prots.items():
            pdsc = pep_prot['dsc']
            if self.proteins[pid] and self.proteins[pid]['LPQ']:
                s = self.proteins[pid]['LPQ']
                if s not in scores:
                    scores[s] = [{ 'id': pid, 'dsc': pdsc }]
                else:
                    scores[s].append({ 'id': pid, 'dsc': pdsc })
        if scores:
            # get the highest score
            hsc = sorted( scores, reverse=True)[0]
            hprot = scores[hsc] 
            # if there are more than one proptein, we have to make a decision
            if len(hprot) == 1:
                hprot = hprot[0]                
            elif len(hprot) > 1:
                hprot = self._unique_protein_decision(hprot)
            # create list with the peptide solution
            rst = hprot['dsc']

        return rst

    def get_unique_protein(self):
        '''
        Calculate the unique protein from the list of peptides
        '''
        results = []
        results_sprest = []
        # extract the LPQ scores for each protein based on the peptide list
        for pep_seq,pep in sorted( self.peptides.items() ):
            pep_prots = pep['proteins']
            pep_species = pep['species']

            # divide the results by species if apply
            hprot = None
            hprot_sprest = None
            if (self.species is not None):
                if ( (self.species in pep_species) and (len(pep_species) == 1) ):
                    hprot = self._unique_protein(pep_prots)
                else:
                    hprot_sprest = self._unique_protein(pep_prots)
            else:
                hprot = self._unique_protein(pep_prots)      
            if hprot:
                results.append([hprot, pep_seq])
            if hprot_sprest:
                results_sprest.append([hprot_sprest, pep_seq])
        # create dataframe with the peptide solution        
        self.rst = pandas.DataFrame(results) # with the given species
        self.rst_sprest = pandas.DataFrame(results_sprest) # witht the rest of species

    def to_csv(self,outfile):
        '''
        Print to file... in principle, in TSV
        '''
        if self.rst is not None and not self.rst.empty:
            self.rst.to_csv(outfile, header=self.rst_header, sep="\t", index=False)
        if self.rst_sprest is not None and not self.rst_sprest.empty:
            outfile = os.path.splitext(outfile)[0] + ".rest_species.txt"
            self.rst_sprest.to_csv(outfile, header=self.rst_header, sep="\t", index=False)

 
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
    methods = ["aljamia1"]
    for method in methods:
        if not method in args.params:
            _print_exception( 2, "checking the parameters for the {} method".format(method) )
        match = re.search(r'{\s*' + method + r'\s*:\s*([^\}]*)}', args.params, re.IGNORECASE)
        if match.group():
            params[method] = match.group(1)
        else:
            _print_exception( 2, "checking the parameters for the {} method".format(method) )

    # get directory from input files
    outdir = os.path.dirname(os.path.realpath(args.relfile))

    # create builder ---
    logging.info("create workflow builder")
    w = wf.builder(outdir, logging)

    logging.info("aljamia for peptide to protein")
    w.aljamia({
        "-x": args.idqfile,
        "-o": "p2q_rels_aux.xls"
    }, params["aljamia1"])

    logging.info('create corrector object')
    co = corrector(w.tmpdir+"/p2q_rels_aux.xls", args.species, args.pretxt, args.indb)

    logging.info('calculate the unique protein')
    co.get_unique_protein()
    
    logging.info('print output')
    co.to_csv(args.relfile)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(
        description='Create the relationship table for peptide2protein method (get unique protein)',
        epilog='''
        Example:
            rel2pq_unique.py -i 
            -r 
            -s 
        Parameter example:
            "{aljamia1: -i [FASTAProteinDescription] -j [Sequence] -k [Redundances] }"
        ''')
    parser.add_argument('-i',  '--idqfile',  required=True, help='ID-q input file')
    parser.add_argument('-r',  '--relfile',  required=True, help='Output file with the relationship table')

    parser.add_argument('-s',  '--species', help='First filter based on the species name')
    parser.add_argument('-t',  '--pretxt', nargs='+', type=str, help='in the case of a tie, we apply teh preferenced text checked in the comment line of a protein. Eg. Organism, etc.')
    parser.add_argument('-d',  '--indb',  help='in the case of a tie, we apply the sorted protein sequence using the given FASTA file')

    parser.add_argument('-a',  '--params',  required=True, help='Input parameters for the sub-methods')
    parser.add_argument('-l',  '--logfile',  help='Output file with the log tracks')
    parser.add_argument('-v', dest='verbose', action='store_true', help="Increase output verbosity")
    args = parser.parse_args()

    # set-up logging
    scriptname = os.path.splitext( os.path.basename(__file__) )[0]

    # init logfile
    logfile = os.path.basename(args.relfile) + "/"+ scriptname +".log"
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
