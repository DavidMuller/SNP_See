import StringIO
from Bio import Entrez
from Bio import SeqIO


def parse_SNP_genotype(SNP_ID_plus_genotype):
    """Given a SNP ID like rs671(T;T), return the genotype of TT"""
    SNP_ID_plus_genotype = SNP_ID_plus_genotype.strip()
    no_closing_parentheses = SNP_ID_plus_genotype.strip(")")
    rsID, genotype = no_closing_parentheses.split("(")
    parent1, parent2 = genotype.split(";")
    return parent1 + parent2


def return_SNP_ID(SNP_ID_plus_genotype):
    """Given a SNP ID like rs671(T;T), return the id of rs671"""
    SNP_ID_plus_genotype = SNP_ID_plus_genotype.strip()
    rsID, genotype = SNP_ID_plus_genotype.split("(")
    return rsID


class SNP_Fetcher:
    """Fetch SNP sequences from NCBI Entrez service, store sequence information.

    Use Entrez efetch to grab sequence data for a given SNP ID.  Store, the SNP
    position, the SNP character, and the flanking sequences.
    Just use set_SNP() to fetch of all the fields in __init__
    """
    def __init__(self):
        Entrez.email = "dmuller@ucsd.edu"
        self.left_flank = None
        self.right_flank = None
        self.left_flank_25_chars = None
        self.right_flank_25_chars = None
        self.SNP = None
        self.SNP_pos = None
        self.SNP_Fasta_string= None
        self.fetched_SNP_ID = None
        self.fasta_separator = "|"

    def set_SNP(self, SNP_ID):
        """Given a SNP ID, fetch the sequence, fill out all SNP Class fields."""
        self.SNP_Fasta_string = self.fetch_SNP_Fasta_string(SNP_ID)
        self.set_SNP_fields(self.SNP_Fasta_string)

    def fetch_SNP_Fasta_string(self, SNP_ID):
        """Fetch Fasta sequence--as a string--for a given SNP ID from NCBI."""
        SNP_fasta_handle = Entrez.efetch(db="snp", id=SNP_ID, rettype="fasta", retmode="text")
        SNP_fasta = SNP_fasta_handle.read()
        return SNP_fasta

    def is_SNP_description(self, description):
        """Return True if descritpion starts with 'pos' or 'allelePos'

        'pos' or 'allelePos' indicate the position of a SNP in a Fasta
        header.
        """
        pos = description.startswith("pos")
        allelePos = description.startswith("allelePos")
        return pos or allelePos

    def find_SNP_pos_in_seqio_record(self, record):
        """Given a SeqIO record object, return the position of the SNP."""
        fields = record.description.split(self.fasta_separator)
        for field in fields:
            if self.is_SNP_description(field):
                pos_number = field.split("=")  # either pos=SOME_NUMBER or allelePos=SOME_NUMBER
                if len(pos_number) > 1:
                    if len(pos_number[1]) > 0:
                        return int(pos_number[1])

    def set_SNP_fields(self, fasta_string):
        """Given ONE Fasta sequence as a string, set SNP's field's."""
        fasta_file = StringIO.StringIO(fasta_string)
        record = SeqIO.read(fasta_file, "fasta")
        self.SNP_pos = self.find_SNP_pos_in_seqio_record(record)
        self.left_flank = record.seq[0:self.SNP_pos - 1]
        self.SNP = record.seq[self.SNP_pos-1]
        self.right_flank = record.seq[self.SNP_pos:]
        self.left_flank_25_chars = self.left_flank[-25:]
        self.right_flank_25_chars = self.right_flank[0:25]