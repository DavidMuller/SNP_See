from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from SNP_Feature_View.models import SNP, SNPStatus, SampleFile

import pickle
import vcf
import os
import sys


class Command(BaseCommand):
    help = 'For every file in our SampleFile database, pull out the genotypes for SNPs in our SNP database. Pickle them to files we can use as session data.'

    def handle(self, *args, **options):
    	sample_files = SampleFile.objects.all()
    	for sample in sample_files:
    		file_name = sample.url()
    		self.stdout.write('Reading %s for SNPs...' % file_name)
    		SessionDataGenerator(file_name, sample.file_type)
	

class SessionDataGenerator():
	def __init__(self, file_name, file_type):
		"""Define path to sample files, and a path to the new session data files. Determine if file is VCF or 23+Me."""
		self.raw_data_file_dir = 'media/SNP_Feature_View/sample_files/'
		self.raw_data_file_path = self.raw_data_file_dir + file_name

		self.session_data_file_dir = 'media/SNP_Feature_View/sample_files_as_session_data/'
		self.session_data_file_path = self.session_data_file_dir + file_name

		# fill out a SNP calls dictionary
		self.SNP_calls = dict()

		if file_type == "VCF":
			self.fill_SNP_calls_dict_vcf()
		else: # 23+Me
			self.fill_SNP_calls_dict_23_and_me()

		# write SNP calls into session data file
		self.write_session_data_file()

	def fill_SNP_calls_dict_vcf(self):
		"""Read the vcf file at self.raw_data_file_path, grab any SNP calls that are also in our database."""
		
		# dump all User-Submitted and Admin-Approved SNPs 
		SNPs_to_look_for = SNP.objects.filter(Q(snpstatus__status='A') | Q(snpstatus__status='U'))
		
		# put SNP ids in a dictionary for fast lookup
		SNPs_to_look_for_dict = dict()
		for s in SNPs_to_look_for:
			snp_name = s.SNP_ID
			if snp_name not in SNPs_to_look_for_dict:
				SNPs_to_look_for_dict[snp_name] = True

		vcf_reader = vcf.Reader(open(self.raw_data_file_path), 'r')
		for record in vcf_reader:
			if record.ID in SNPs_to_look_for_dict:
				call = record.genotype(vcf_reader.samples[0])
				bases = call.gt_bases[0] + call.gt_bases[2]  #just save GG, not something like G/G				self.SNP_calls[record.ID] = bases
				self.SNP_calls[record.ID] = bases

	def fill_SNP_calls_dict_23_and_me(self):
		"""Read the 23+Me file at self.raw_data_file_path, grab any SNP calls that are also in our database."""
		
		# dump all User-Submitted and Admin-Approved SNPs 
		SNPs_to_look_for = SNP.objects.filter(Q(snpstatus__status='A') | Q(snpstatus__status='U'))
		
		# put SNP ids in a dictionary for fast lookup
		SNPs_to_look_for_dict = dict()
		for s in SNPs_to_look_for:
			snp_name = s.SNP_ID
			if snp_name not in SNPs_to_look_for_dict:
				SNPs_to_look_for_dict[snp_name] = True
		
		with open(self.raw_data_file_path, 'r') as handle:
			for line in handle:
				if line.startswith("#") == False: #skip comment lines 
					line = line.rstrip("\n\r")
					line = line.rstrip()
					rs_id, chrom, chrom_pos, genotype = line.split("\t")
					if rs_id in SNPs_to_look_for_dict:
						self.SNP_calls[rs_id] = genotype

	def write_session_data_file(self):
		"""Pickle the SNP_calls dict to a file."""
		with open(self.session_data_file_path, 'w') as handle:
			pickle.dump(self.SNP_calls, handle)	