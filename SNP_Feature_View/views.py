from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.conf import settings

from SNP_Feature_View.models import Phenotype, Pheno_Geno_Morphology, SNP, SampleFile
from SNP import parse_SNP_genotype, return_SNP_ID, SNP_Fetcher

import os
import pickle
import vcf

def index(request):
    print settings.BASE_DIR
    return render(request, 'SNP_Feature_View/index.html')


def about(request):
    return render(request, 'SNP_Feature_View/about.html')


def contact(request):
    return render(request, 'SNP_Feature_View/contact.html')


def under_construction(request):
    return render(request, 'SNP_Feature_View/under_construction.html')


def feature_view_home(request):
    return render(request, 'SNP_Feature_View/feature_view_home.html')


def feature_view_sample_data_selector(request):
    sample_files = SampleFile.objects.all()
    context = {'sample_files':sample_files}
    return render(request, 'SNP_Feature_View/sample_data.html', context)


def feature_view_load_session_data(request, file_name):
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""
    """CHECK THAT THE FILE IS VALID....DID YOU GET THIS FROM OUR PAGE...REPORT AN ERROR."""

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
    phenotypes = Phenotype.objects.all()
    context = {'phenotypes':phenotypes}
    return render(request, 'SNP_Feature_View/select_phenotypes.html', context)


def feature_view(request, phenotype_pk):
    phenotype = Phenotype.objects.get(pk=phenotype_pk)
    pheno_geno_morphology = Pheno_Geno_Morphology.objects.all().filter(phenotype__exact=phenotype)
    sf = SNP_Fetcher()

    for key in request.session.keys():
        print key,request.session[key]

    # loop through, see if we match on a genotype
    for row in pheno_geno_morphology:
        SNP_ID = return_SNP_ID(row.genotype)
        genotype = parse_SNP_genotype(row.genotype)
        if SNP_ID in request.session['SNPs']:
            if request.session['SNPs'][SNP_ID] == genotype:
                snp = SNP.objects.get(SNP_ID__exact=SNP_ID)
                sf.set_SNP_fields(snp.fasta_sequence)
                file_name = request.session['SNPs']['file_name']
                file_size = request.session['SNPs']['file_size']

                context = {'file_name':file_name, 'file_size':file_size, 'phenotype': phenotype, 'pheno_geno_morphology':row, 'sf':sf, 'snp_chars':genotype}
                return render(request, 'SNP_Feature_View/feature_view.html', context)

    return feature_view_not_enough_data(request, phenotype_pk)


def feature_view_not_enough_data(request, phenotype_pk):
    phenotype = Phenotype.objects.get(pk=phenotype_pk)
    file_name = request.session['SNPs']['file_name']
    context = {'file_name':file_name, 'phenotype': phenotype}
    return render(request, 'SNP_Feature_View/not_enough_data.html', context)




def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')