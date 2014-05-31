from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.conf import settings

from SNP_Feature_View.models import Phenotype, Pheno_Geno_Morphology, SNP, SampleFile
from SNP import parse_SNP_genotype, return_SNP_ID, SNP_Fetcher

import os
import pickle
import vcf
import copy


def index(request):
    """Home page."""
    return render(request, 'SNP_Feature_View/index.html')


def about(request):
    """About page."""
    return render(request, 'SNP_Feature_View/about.html')


def contact(request):
    """Contact page."""
    return render(request, 'SNP_Feature_View/contact.html')


def under_construction(request):
    """Under construction page."""
    return render(request, 'SNP_Feature_View/under_construction.html')


def feature_view_home(request):
    """Feature view home page."""
    return render(request, 'SNP_Feature_View/feature_view_home.html')


def data_set_characterization(request):
    """Data set characterization page."""
    return render(request, 'SNP_Feature_View/data_set_characterization.html')


def feature_view_sample_data_selector(request):
    """Choose a file for viewing."""
    file_name = "None"
    if 'SNPs' in request.session:
        file_name = request.session['SNPs']['file_name']

    sample_files = SampleFile.objects.all()
    context = {'sample_files':sample_files, 'file_name':file_name}
    return render(request, 'SNP_Feature_View/sample_data.html', context)


def feature_view_load_session_data(request, file_name):
    """Load a chosen file's SNP calls into session data store."""
    # clear previous SNP data
    if 'SNPs' in request.session:
        del request.session['SNPs']

    # save other session data that isn't SNP related
    copy_session = dict(request.session)  

    with open('media/SNP_Feature_View/sample_files_as_session_data/' + file_name
, 'rb') as handle:
        SNPs_dict = pickle.loads(handle.read())
    
    statinfo = os.stat('media/SNP_Feature_View/sample_files/' + file_name)

    request.session['SNPs'] = SNPs_dict 
    request.session['SNPs']['file_name'] = file_name
    request.session['SNPs']['file_size'] = sizeof_fmt(statinfo.st_size)

    return feature_view_select_phenotypes(request)


def feature_view_select_phenotypes(request):
    """Display all phenotypes available for viewing."""
    phenotypes = Phenotype.objects.all()
    context = {'phenotypes':phenotypes}
    return render(request, 'SNP_Feature_View/select_phenotypes.html', context)


def visual_browser(request, chromosome_num, highlight):
    """JBrowse viewer.  chromosome_num and highlight specify where to zoom/highlight."""
    # make sure the user has selected a file
    if 'SNPs' not in request.session:
        return render(request, 'SNP_Feature_View/woops_select_a_file.html')

    JBrowse_arg_string = ""
    if highlight != "None" and chromosome_num != "None":
        region = "chr" + chromosome_num + ":" + highlight # eg chr1:1200
        JBrowse_arg_string = "&highlight=" + region + "&loc=" + region

    file_name = request.session['SNPs']['file_name']
    file_size = request.session['SNPs']['file_size']
    context = {'file_name':file_name, 'file_size':file_size, 'JBrowse_arg_string':JBrowse_arg_string }
    return render(request, 'SNP_Feature_View/visual_browser.html', context)


def feature_view(request, phenotype):
    """Standard phenotype page."""

    # make sure the user has selected a file
    if 'SNPs' not in request.session:
        return render(request, 'SNP_Feature_View/woops_select_a_file.html')

    phenotype = phenotype.replace("_", " ") #JBrowse passes phenotypes with underscores
    phenotype = Phenotype.objects.get(phenotype=phenotype)
    pheno_geno_morphology = Pheno_Geno_Morphology.objects.all().filter(phenotype__exact=phenotype)
    sf = SNP_Fetcher()

    # loop through, see if we match on a genotype
    for row in pheno_geno_morphology:
        SNP_ID = return_SNP_ID(row.genotype)
        genotype = parse_SNP_genotype(row.genotype)
        if SNP_ID in request.session['SNPs']:
            if request.session['SNPs'][SNP_ID] == genotype:
                snp = SNP.objects.get(SNP_ID__exact=SNP_ID)
                
                sf.set_SNP_fields(snp.fasta_sequence)

                # if the snp fasta sequence is on the '-' strand, adjust appropriately
                if snp.strand == "-":
                    temp_left = copy.deepcopy(sf.left_flank_25_chars)
                    sf.left_flank_25_chars = sf.right_flank_25_chars
                    sf.right_flank_25_chars = temp_left
                    sf.left_flank_25_chars = sf.left_flank_25_chars[::-1]
                    sf.right_flank_25_chars = sf.right_flank_25_chars[::-1]
                
                file_name = request.session['SNPs']['file_name']
                file_size = request.session['SNPs']['file_size']

                context = {'file_name':file_name, 'file_size':file_size, 'phenotype': phenotype, 'pheno_geno_morphology':row, 'sf':sf, 'snp_chars':genotype}
                return render(request, 'SNP_Feature_View/feature_view.html', context)

    return feature_view_not_enough_data(request, phenotype)


def feature_view_within_visual_browser(request, phenotype):
    """Phenotype page rendered below JBrowse."""
    phenotype = phenotype.replace("_", " ")
    phenotype = Phenotype.objects.get(phenotype=phenotype)
    pheno_geno_morphology = Pheno_Geno_Morphology.objects.all().filter(phenotype__exact=phenotype)
    sf = SNP_Fetcher()

    # loop through, see if we match on a genotype
    for row in pheno_geno_morphology:
        SNP_ID = return_SNP_ID(row.genotype)
        genotype = parse_SNP_genotype(row.genotype)
        if SNP_ID in request.session['SNPs']:
            if request.session['SNPs'][SNP_ID] == genotype:
                snp = SNP.objects.get(SNP_ID__exact=SNP_ID)
                
                sf.set_SNP_fields(snp.fasta_sequence)

                # if the snp fasta sequence is on the '-' strand, adjust appropriately
                if snp.strand == "-":
                    temp_left = copy.deepcopy(sf.left_flank_25_chars)
                    sf.left_flank_25_chars = sf.right_flank_25_chars
                    sf.right_flank_25_chars = temp_left
                    sf.left_flank_25_chars = sf.left_flank_25_chars[::-1]
                    sf.right_flank_25_chars = sf.right_flank_25_chars[::-1]

                file_name = request.session['SNPs']['file_name']
                file_size = request.session['SNPs']['file_size']

                context = {'file_name':file_name, 'file_size':file_size, 'phenotype': phenotype, 'pheno_geno_morphology':row, 'sf':sf, 'snp_chars':genotype}
                return render(request, 'SNP_Feature_View/feature_view_visual_browser.html', context)

    return feature_view_within_visual_browser_not_enough_data(request, phenotype)


def feature_view_not_enough_data(request, phenotype):
    """Display if the necessary SNP calls are not present."""
    file_name = request.session['SNPs']['file_name']
    context = {'file_name':file_name, 'phenotype': phenotype}
    return render(request, 'SNP_Feature_View/not_enough_data.html', context)


def feature_view_within_visual_browser_not_enough_data(request, phenotype):
    """Display below JBrowse if the necessary SNP calls are not present."""
    file_name = request.session['SNPs']['file_name']
    context = {'file_name':file_name, 'phenotype': phenotype}
    return render(request, 'SNP_Feature_View/not_enough_data_visual_browser.html', context)


def sizeof_fmt(num):
    """Return a human readable file size."""
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')