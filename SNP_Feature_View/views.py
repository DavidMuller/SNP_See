from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models import Count
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.management import call_command

from SNP_Feature_View.models import Phenotype, Pheno_Geno_Morphology, SNP, SampleFile, SAMPLE_FILES_DIR, SNPStatus, PhenotypeStatus
from SNP import parse_SNP_genotype, return_SNP_ID, SNP_Fetcher
from forms import validate_fasta, validate_phenotype_name, validate_snp_id, AddFeature, EditIncomplete

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


def heads_up(request):
    """Generic error page."""
    return render(request, 'SNP_Feature_View/heads_up.html')


def under_construction(request):
    """Under construction page."""
    return render(request, 'SNP_Feature_View/under_construction.html')


def feature_view_home(request):
    """Feature view home page."""
    return render(request, 'SNP_Feature_View/feature_view_home.html')


def data_set_detail(request, chromosome_num):
    """Data Set Details Page (List features maintained on a given chromosome)"""
    # make sure we have features on that chromosome 
    try:
        traits_admin = SNP.objects.filter(snpstatus__status='A', chromosome_num=chromosome_num)
        traits_user = SNP.objects.filter(snpstatus__status='U', chromosome_num=chromosome_num)

    except:
        return heads_up(request)

    context = {'traits_admin':traits_admin, 'traits_user':traits_user, 'chromosome_num':chromosome_num}
    return render(request, 'SNP_Feature_View/data_set_detail.html', context)


def data_set_characterization(request):
    """Data set characterization page."""
    admin_approved = Phenotype.objects.filter(phenotypestatus__status='A')
    user_submitted = Phenotype.objects.filter(phenotypestatus__status='U')
    sample_files = SampleFile.objects.all()

    admin_approved_count = len(admin_approved)
    user_submitted_count = len(user_submitted)

    traits_by_chrom = SNP.objects.filter(Q(snpstatus__status='A') | Q(snpstatus__status='U')).values('chromosome_num').annotate(num_traits=Count('chromosome_num'))

    context = {'user_submitted_count':user_submitted_count,
               'admin_approved_count':admin_approved_count,
               'sample_files':sample_files,
               'traits_by_chrom':traits_by_chrom}

    return render(request, 'SNP_Feature_View/data_set_characterization.html', context)


def feature_view_sample_data_selector(request):
    """Choose a file for viewing."""
    # file_name is name of "currently selected" file 
    file_name = "None" 
    if 'SNPs' in request.session:
        file_name = request.session['SNPs']['file_name']

    sample_files = SampleFile.objects.all()
    context = {'sample_files':sample_files, 'file_name':file_name}
    return render(request, 'SNP_Feature_View/sample_data.html', context)


def feature_view_load_session_data(request, file_name):
    """Load a chosen file's SNP calls into session data store."""
    # make sure we have a file with the given name
    try:
        file_to_load = SampleFile.objects.get(sample_file=SAMPLE_FILES_DIR + file_name)
    except:
        return heads_up(request)

    # clear previous SNP data
    if 'SNPs' in request.session:
        del request.session['SNPs'] 

    # read in the specified file
    with open(os.path.join(settings.BASE_DIR, 'media/SNP_Feature_View/sample_files_as_session_data/' + file_name), 'rb') as handle:
        SNPs_dict = pickle.load(handle)
    
    request.session['SNPs'] = SNPs_dict 
    request.session['SNPs']['file_name'] = str(file_to_load.url())
    request.session['SNPs']['file_size'] = str(file_to_load.readable_size())

    return feature_view_select_phenotypes(request)


def feature_view_select_phenotypes(request):
    """Display all phenotypes available for viewing (User-submitted, and Admin Approved.)"""
    user_submitted = Phenotype.objects.filter(phenotypestatus__status='U')
    admin_approved = Phenotype.objects.filter(phenotypestatus__status='A')
    context = {'user_submitted':user_submitted, 'admin_approved':admin_approved}
    return render(request, 'SNP_Feature_View/select_phenotypes.html', context)


def visual_browser(request, chromosome_num, highlight):
    """JBrowse viewer.  

    chromosome_num and highlight specify where to zoom/highlight.
    """
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
    """Standard phenotype feature view page."""
    # make sure the user has selected a file
    if 'SNPs' not in request.session:
        return render(request, 'SNP_Feature_View/woops_select_a_file.html')

    # make sure we have the requested phenotype
    try:
        phenotype = phenotype.replace("_", " ") #JBrowse passes phenotypes with underscores
        phenotype = Phenotype.objects.get(Q(phenotypestatus__status='A') | Q(phenotypestatus__status='U'), phenotype=phenotype)
        status = phenotype.phenotypestatus_set.get(associated_phenotype=phenotype).status
        pheno_geno_morphology = Pheno_Geno_Morphology.objects.all().filter(phenotype__exact=phenotype)
    except:
        return heads_up(request)

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

                context = {'file_name':file_name, 'file_size':file_size, 'phenotype': phenotype, 'pheno_geno_morphology':row, 'sf':sf, 'snp_chars':genotype, 'status':status}
                return render(request, 'SNP_Feature_View/feature_view.html', context)

    return feature_view_not_enough_data(request, phenotype)


def feature_view_within_visual_browser(request, phenotype):
    """Phenotype page rendered below JBrowse."""
    # make sure the user has selected a file
    if 'SNPs' not in request.session:
        return render(request, 'SNP_Feature_View/woops_select_a_file.html')

    # make sure we have the requested phenotype
    try:
        phenotype = phenotype.replace("_", " ") #JBrowse passes phenotypes with underscores
        phenotype = Phenotype.objects.get(phenotype=phenotype, phenotypestatus__status='A')
        pheno_geno_morphology = Pheno_Geno_Morphology.objects.all().filter(phenotype__exact=phenotype)

    except:
        return heads_up(request)

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


# NEW FEATURE CREATION:

def add_new_feature_home(request):
    """Home page for adding new features."""
    return render(request, 'SNP_Feature_View/add_new_feature_home.html')


def unavailable_for_editing(request):
    """Return this page if a phenotype is not available to be edited.

    Phenotypes are only available for editing if they are 'Incomplete.'
    """
    return render(request, 'SNP_Feature_View/unavailable_for_editing.html')


def thanks(request):
    """Thank you page for completion of a user-submitted feature.

    Inform the user that their SNP can now be found in the SNP See 
    list phenotype page.
    """
    return render(request, 'SNP_Feature_View/thanks.html')


def incomplete_user_submissions(request):
    """List all phenotypes that are 'Incomplete.'

    Make them available to edit via a click.
    """
    incomplete = Phenotype.objects.filter(phenotypestatus__status='I')
    context = {'incomplete':incomplete }
    return render(request, "SNP_Feature_View/incomplete_user_submissions.html", context)


def add_new(request):
    """Initial feature creation form.

    Choose the phenotype name, SNP id, and fill in initial SNP properties.
    """
    if request.method == 'POST': # If the form has been submitted...
        form = AddFeature(request.POST) # A form bound to the POST data

        if form.is_valid(): # All validation rules pass
            phenotype_name = form.cleaned_data['phenotype_name']
            snp_id = form.cleaned_data['snp_id']
            flanking_sequence = form.cleaned_data['flanking_sequence']
            flanking_sequence_strand = form.cleaned_data['flanking_sequence_strand']
            chrom_num = form.cleaned_data['chromosome_num']
            chrom_pos = form.cleaned_data['chromosome_pos_GRCh37']

            p = Phenotype(phenotype=phenotype_name)
            p.save()

            s = SNP(
                SNP_ID=snp_id, 
                fasta_sequence=flanking_sequence, 
                strand=flanking_sequence_strand, 
                chromosome_num=chrom_num, 
                chromosome_pos_GRCh37=chrom_pos, 
                associated_phenotype=p)
            s.save()

            p.associated_snps.add(s)
            p.save()

            ps = PhenotypeStatus(associated_phenotype=p, status='I')
            ps.save()

            ss = SNPStatus(associated_snp=s, status='I')
            ss.save()

            return redirect('incomplete_user_submissions')# Redirect after POST
    else:
        form = AddFeature() # An unbound form

    return render(request, 'SNP_Feature_View/add_new.html', {
        'form': form,
    })


def edit_incomplete(request, phenotype):
    """Edit an incomplete feature.

    Allow edits to SNP properties (not ID!), about text, external resources, and genotypes.
    """
    try:
        incomplete = Phenotype.objects.get(phenotype=phenotype, phenotypestatus__status='I')
        associated_snp = incomplete.associated_snps.all()[0]
        s = SNP.objects.get(SNP_ID__exact=associated_snp)
    except:
        return redirect('unavailable_for_editing')        

    if request.method == 'POST': # If the form has been submitted...

        form = EditIncomplete(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            s.fasta_sequence = form.cleaned_data['flanking_sequence']
            s.strand = form.cleaned_data['flanking_sequence_strand']
            s.chromosome_num = form.cleaned_data['chromosome_num']
            s.chromosome_pos_GRCh37 = form.cleaned_data['chromosome_pos_GRCh37']
            s.save()

            incomplete.about_phenotype_text = form.cleaned_data['about_text']
            incomplete.external_resources = form.cleaned_data['external_resources']
            incomplete.save()

            genotype1 = form.cleaned_data["genotype1"]
            genotype2 = form.cleaned_data["genotype2"]
            genotype3 = form.cleaned_data["genotype3"]
            genotype4 = form.cleaned_data["genotype4"]

            about_genotype1 = form.cleaned_data["about_genotype1"]
            about_genotype2 = form.cleaned_data["about_genotype2"]
            about_genotype3 = form.cleaned_data["about_genotype3"]
            about_genotype4 = form.cleaned_data["about_genotype4"]

            genotypes = [genotype1, genotype2, genotype3, genotype4]
            about = [about_genotype1, about_genotype2, about_genotype3, about_genotype4]
            all_genotype_data = zip(genotypes, about)

            for element in all_genotype_data:
                genotype = element[0]
                about_text = element[1]
                if (genotype != "") and (about_text != ""):
                    # db_string is something like rs671(A;A)
                    genotype_string = str(associated_snp) + "(" + genotype[0] + ";" + genotype[1] + ")"
                    pgm = Pheno_Geno_Morphology(phenotype=incomplete, genotype=genotype_string, morphology=about_text)
                    pgm.save()

            
            ps = PhenotypeStatus.objects.get(associated_phenotype=incomplete)
            ps.status = 'U'
            ps.save()

            ss = SNPStatus.objects.get(associated_snp=s)
            ss.status = 'U'
            ss.save()

            return redirect('thanks') # Redirect after POST
    
    else:
        form = EditIncomplete(initial={'flanking_sequence':s.fasta_sequence,
                                      'flanking_sequence_strand': s.strand,
                                      'chromosome_num': s.chromosome_num,
                                      'chromosome_pos_GRCh37': s.chromosome_pos_GRCh37
                                 }) 

    fields = list(form)
    snp_fields = fields[0:4]
    phenotype_fields = fields[4:6]
    pgm_field = fields[6:8]
    optional_pgm_fields = fields[8:]
    return render(request, 'SNP_Feature_View/edit_incomplete.html', {
        'snp_fields': snp_fields,
        'phenotype_fields': phenotype_fields,
        'pgm_field': pgm_field,
        'optional_pgm_fields': optional_pgm_fields,
        'phenotype_name':phenotype,
        'snp_name': associated_snp,
        'form':form
    })
