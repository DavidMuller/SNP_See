from django.db import models
from django.conf import settings

import os


class Phenotype(models.Model):
    """Hold the high level trait, its associated SNPs, and text about it."""
    phenotype = models.CharField(max_length=70, unique=True)
    about_phenotype_text = models.TextField(blank=True)
    external_resources = models.TextField(blank=True)
    associated_snps = models.ManyToManyField('SNP', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.phenotype)


class Pheno_Geno_Morphology(models.Model):
    """For a given phenotype (high level trait), save possible genotypes, and their morphologies."""
    phenotype = models.ForeignKey(Phenotype)
    genotype = models.TextField()
    morphology = models.TextField()

    class Meta:
        # for a given phenotype, no duplicate genotypes
        unique_together = ["phenotype", "genotype"]

    def __unicode__(self):
        return u'%s' % (self.phenotype)


class SNP(models.Model):
    """Store SNPs by rsID.  Keep associated sequence, and position + flanking sequence for GRCh37."""
    # to be stored in database
    FORWARD = '+'
    REVERSE = '-'

    # human readable
    STRAND_CHOICES = (
        (FORWARD, 'Forward'),
        (REVERSE, 'Reverse'),
    )
    
    SNP_ID = models.CharField(max_length=70, unique=True, db_index=True)
    fasta_sequence = models.TextField()
    strand = models.CharField(max_length=1, choices=STRAND_CHOICES, default=FORWARD)
    chromosome_num = models.IntegerField()
    chromosome_pos_GRCh37 = models.IntegerField()
    associated_phenotype = models.ForeignKey(Phenotype, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.SNP_ID)


SAMPLE_FILES_DIR = settings.MEDIA_ROOT + "SNP_Feature_View/sample_files/"

class SampleFile(models.Model):
    """Sample files for browsing.

    Store their path, file type, and some associated text.
    """
    # to be stored in database
    VCF = 'VCF'
    TWENTYTHREEANDME = '23+Me'
    OTHER = 'other'

    # human readable
    FILE_TYPE_CHOICES = (
        (VCF, 'VCF_File'),
        (TWENTYTHREEANDME, '23_And_Me_File'),
        (OTHER, 'other'),
    )

    sample_file = models.FilePathField(path=SAMPLE_FILES_DIR, unique=True, db_index=True)
    file_type = models.CharField(max_length=5, choices=FILE_TYPE_CHOICES, default=VCF)
    source = models.TextField()
    fun_fact = models.TextField()

    def url(self):
        """Return file name."""
        path = self._meta.get_field('sample_file').path
        return self.sample_file.replace(path, '', 1)

    def size(self):
        """Return size in bytes."""
        statinfo = os.stat(self.sample_file)
        return statinfo.st_size

    def readable_size(self):
        """Return a human readable file size."""
        statinfo = os.stat(self.sample_file)
        return sizeof_fmt(statinfo.st_size)

    def __unicode__(self):
        return u'%s' % (self.sample_file)


class PhenotypeStatus(models.Model):
    """Status of af given phenotype.

    Admin approved, user-submitted, or incomplete.
    """
    # to be stored in database
    ADMIN_APPROVED = 'A'
    USER_SUBMITTED = 'U'
    INCOMPLETE = 'I'

    # human readable
    STATUS_CHOICES = (
        (ADMIN_APPROVED, 'Administrator Approved'),
        (USER_SUBMITTED, 'User Submitted'),
        (INCOMPLETE, 'Incomplete'),
    )

    associated_phenotype = models.ForeignKey(Phenotype, unique=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=INCOMPLETE)


class SNPStatus(models.Model):
    """Status of af given SNP.

    Admin approved, user-submitted, or incomplete.
    """
    # to be stored in database
    ADMIN_APPROVED = 'A'
    USER_SUBMITTED = 'U'
    INCOMPLETE = 'I'

    # human readable
    STATUS_CHOICES = (
        (ADMIN_APPROVED, 'Administrator Approved'),
        (USER_SUBMITTED, 'User Submitted'),
        (INCOMPLETE, 'Incomplete'),
    )

    associated_snp = models.ForeignKey(SNP, unique=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=INCOMPLETE)


def sizeof_fmt(num):
    """Given number of bytes, return human readable file size."""
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')