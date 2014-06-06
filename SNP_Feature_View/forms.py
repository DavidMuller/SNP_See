from django import forms
from django.core.exceptions import ValidationError
from SNP_Feature_View.models import Phenotype, Pheno_Geno_Morphology, SNP, SampleFile, SNPStatus, PhenotypeStatus
from SNP import parse_SNP_genotype, return_SNP_ID, SNP_Fetcher

from Bio import SeqIO
import StringIO


def validate_fasta(fasta_string):
    """Validate the fasta sequence input for SNPs.

    Must actually be a fasta string, must specify a snp positon, must have
    at least 25 bases on each side of the SNP.
    """
    fasta_file = StringIO.StringIO(fasta_string) 
    try:
        record = SeqIO.read(fasta_file, "fasta")
        
        if len(record.seq) == 0:
            raise ValidationError(u'No sequence entered.')

        sf = SNP_Fetcher()
        snp_pos = sf.find_SNP_pos_in_seqio_record(record)

        if snp_pos is None:
            raise ValidationError(u'Please specify the position of the SNP allele in the fasta header with pos=some_number or allelePos=some_number.  If you retrieve the fasta sequence from dbsnp, this will be included. eg: >myseq|allelePos=501')

        if snp_pos <=0 or snp_pos > len(record.seq):
            raise ValidationError(u'In your fasta header, please use a valid position for the SNP in your sequence (pos=some_number or allelePos=some_number).')

        if snp_pos < 25:
            raise ValidationError(u'SNP See requires at least 25 flanking bases on each side of the SNP.')

        if (snp_pos + 25) > len(record.seq):
            raise ValidationError(u'SNP See requires at least 25 flanking bases on each side of the SNP.')

    except ValueError:
        raise ValidationError(u'Not a valid fasta string.')


def validate_phenotype_name(phenotype_name):
    """A new phenotype can't have the same name as any existing one."""
    try:
        print phenotype_name
        phenotype = Phenotype.objects.get(phenotype=phenotype_name)
        raise ValidationError(u'This feature name is already in use.')
    except Phenotype.DoesNotExist:
        pass


def validate_snp_id(SNP_ID):
    """A new SNP can't have the same ID as any existing one."""
    try:
        snp = SNP.objects.get(SNP_ID__exact=SNP_ID)
        raise ValidationError(u'This SNP is already in our database.  Unfortunately, at this point, we only support associating a SNP with one trait.')
    except SNP.DoesNotExist:
        pass


class AddFeature(forms.Form):
    """Initial add feature form.

    Choose the phenotype name, SNP id, and fill in initial SNP properties.
    """
    error_css_class = 'error'
    required_css_class = 'required'
    
    # to be stored in database
    FORWARD = '+'
    REVERSE = '-'

    # human readable
    STRAND_CHOICES = (
        (FORWARD, 'Forward'),
        (REVERSE, 'Reverse'),
    )

    CHROMOSOME_NUM = (
        (1, 'chr1'),
        (2, 'chr2'),
        (3, 'chr3'),
        (4, 'chr4'),
        (5, 'chr5'),
        (6, 'chr6'),
        (7, 'chr7'),
        (8, 'chr8'),
        (9, 'chr9'),
        (10, 'chr10'),
        (11, 'chr11'),
        (12, 'chr12'),
        (13, 'chr13'),
        (14, 'chr14'),
        (15, 'chr15'),
        (16, 'chr16'),
        (17, 'chr17'),
        (18, 'chr18'),
        (19, 'chr19'),
        (20, 'chr20'),
        (21, 'chr21'),
    )

    phenotype_name = forms.RegexField(regex=r'^[a-zA-Z0-9_ ]+$', 
                                        max_length=70, 
                                        label="Name your feature",
                                        error_messages={'invalid': "White space and alphanumeric characters only."}, 
                                        validators=[validate_phenotype_name])
    
    snp_id = forms.RegexField(regex=r'^rs\d+$', 
                                label="SNP rsID", 
                                initial="rs...", 
                                max_length=70, 
                                validators=[validate_snp_id], 
                                error_messages={'invalid': 'Please enter a SNP rs#, e.g: rs671'})
    
    flanking_sequence = forms.CharField(widget=forms.Textarea(attrs={'rows':7, 'cols':90}), 
                                        label="Fasta sequence surrounding this SNP. Requires 25 bases on each side of SNP. Ideally, get this form dbSNP.", 
                                        validators=[validate_fasta])

    flanking_sequence_strand = forms.ChoiceField(choices=STRAND_CHOICES, 
                                                label="Orientation of fasta sequence relative to GRCh37.")
    
    chromosome_num = forms.ChoiceField(choices=CHROMOSOME_NUM, label="Chrosomse number.")
    
    chromosome_pos_GRCh37 = forms.IntegerField(min_value=0, max_value=300000000, label="GRCh37 (hg19) position of SNP")



class EditIncomplete(forms.Form):
    """Edit an incomplete feature.

    Allow edits to SNP properties (not ID!), about text, external resources, and genotypes.
    """
    error_css_class = 'error'
    required_css_class = 'required'

    # to be stored in database
    FORWARD = '+'
    REVERSE = '-'

    # human readable
    STRAND_CHOICES = (
        (FORWARD, 'Forward'),
        (REVERSE, 'Reverse'),
    )

    CHROMOSOME_NUM = (
        (1, 'chr1'),
        (2, 'chr2'),
        (3, 'chr3'),
        (4, 'chr4'),
        (5, 'chr5'),
        (6, 'chr6'),
        (7, 'chr7'),
        (8, 'chr8'),
        (9, 'chr9'),
        (10, 'chr10'),
        (11, 'chr11'),
        (12, 'chr12'),
        (13, 'chr13'),
        (14, 'chr14'),
        (15, 'chr15'),
        (16, 'chr16'),
        (17, 'chr17'),
        (18, 'chr18'),
        (19, 'chr19'),
        (20, 'chr20'),
        (21, 'chr21'),
    )


    flanking_sequence = forms.CharField(widget=forms.Textarea(attrs={'rows':7, 'cols':90}), 
                                        label="Fasta sequence surrounding this SNP. Requires 25 bases on each side of SNP. Ideally, get this form dbSNP.", 
                                        validators=[validate_fasta])

    flanking_sequence_strand = forms.ChoiceField(choices=STRAND_CHOICES, 
                                                label="Orientation of fasta sequence relative to GRCh37.")
    
    chromosome_num = forms.ChoiceField(choices=CHROMOSOME_NUM, label="Chrosomse number.")
    
    chromosome_pos_GRCh37 = forms.IntegerField(min_value=0, max_value=300000000, label="GRCh37 (hg19) position of SNP")


    about_text = forms.CharField(widget=forms.Textarea(attrs={'rows':5, 'cols':90}), 
                                label="Give a brief summary of the trait/feature associated with the SNP you're adding:")
    
    external_resources = forms.CharField(widget=forms.Textarea(attrs={'rows':5, 'cols':90}), 
                                                                label="Give some more detail on the trait/feature associated with the SNP you're adding (talk about the external resources you used...):")
    
    genotype1 = forms.RegexField(regex=r'^[ATCG][ATCG]$', required=True, label="SNP genotype, e.g: AA, AT", error_messages={'invalid': 'Please enter a genotype using 2 bases (A, T, C, and G) directly in sequence.  Capital letters.  No white space.'})
    about_genotype1 = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows':3, 'cols':50}), label="Discuss the implications of this SNP genotype.  What does the genotype determine at a higher level?")
    
    genotype2 = forms.RegexField(regex=r'^[ATCG][ATCG]$', required=False, label="Optional: add another SNP genotype, e.g: AA, AT", error_messages={'invalid': 'Please enter a genotype using 2 bases (A, T, C, and G) directly in sequence.  Capital letters.  No white space.'})
    about_genotype2 = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'cols':50}), label="If you added a genotype in the box directly above, you must discuss the implications of that genotype here:")
    
    genotype3 = forms.RegexField(regex=r'^[ATCG][ATCG]$', required=False, label="Optional: add another SNP genotype, e.g: AA, AT", error_messages={'invalid': 'Please enter a genotype using 2 bases (A, T, C, and G) directly in sequence.  Capital letters.  No white space.'})
    about_genotype3 = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'cols':50}), label="If you added a genotype in the box directly above, you must discuss the implications of that genotype here:")
    
    genotype4 = forms.RegexField(regex=r'^[ATCG][ATCG]$', required=False, label="Optional: add another SNP genotype, e.g: AA, AT", error_messages={'invalid': 'Please enter a genotype using 2 bases (A, T, C, and G) directly in sequence.  Capital letters.  No white space.'})
    about_genotype4 = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'cols':50}), label="If you added a genotype in the box directly above, you must discuss the implications of that genotype here:")
 
    def clean(self):
        """Check to be sure no duplicate genotypes were entered.

        Also check that submitted genotypes were given a description.
        """
        cleaned_data = super(EditIncomplete, self).clean()
        genotype1 = cleaned_data.get("genotype1")
        genotype2 = cleaned_data.get("genotype2")
        genotype3 = cleaned_data.get("genotype3")
        genotype4 = cleaned_data.get("genotype4")

        about_genotype1 = cleaned_data.get("about_genotype1")
        about_genotype2 = cleaned_data.get("about_genotype2")
        about_genotype3 = cleaned_data.get("about_genotype3")
        about_genotype4 = cleaned_data.get("about_genotype4")

        genotype_dict = dict()
        genotypes = [genotype1, genotype2, genotype3, genotype4]
        about = [about_genotype1, about_genotype2, about_genotype3, about_genotype4]
        all_genotype_data = zip(genotypes, about)

        for element in all_genotype_data:
            genotype = element[0]
            about_text = element[1]
            if genotype != "":
                if genotype in genotype_dict:
                    raise forms.ValidationError("Woops. You've entered the same SNP genotype twice--check the extra genotypes you added in the hidden menu below.")
                else:
                    genotype_dict[genotype] = True

                if about_text == "":
                    raise forms.ValidationError("Woops. You must eneter a description for any genotype you enter.  Be sure to check the extra genotypes you added in the hidden menu below for errors.")

        return cleaned_data