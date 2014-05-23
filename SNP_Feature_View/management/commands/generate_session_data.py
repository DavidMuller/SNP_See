from django.core.management.base import BaseCommand, CommandError
from SNP_Feature_View.models import SNP

import pickle
import vcf
import os
import sys

class Command(BaseCommand):
    args = '<file_name file_name ...>'
    help = 'For every file, pull out the calls for SNPs in our SNP database. Pickle them out to files we can use as session data.'

    def handle(self, *args, **options):
		for file_name in args:
			self.stdout.write('Reading "%s" for SNPs...' % file_name)
			SessionDataGenerator(file_name)



class SessionDataGenerator():
	def __init__(self, file_name):
		self.raw_data_file_dir = 'media/SNP_Feature_View/sample_files/'
		self.raw_data_file_path = self.raw_data_file_dir + file_name

		self.session_data_file_dir = 'media/SNP_Feature_View/sample_files_as_session_data/'
		self.session_data_file_path = self.session_data_file_dir + file_name

		self.SNP_calls = dict()
		self.fill_SNP_calls_dict()
		self.write_session_data_file()

	def fill_SNP_calls_dict(self):
		"""Read the file at self.raw_data_file_path, grab any SNP calls that are also in our database."""
		SNPs_to_look_for = SNP.objects.values_list('SNP_ID', flat=True)
		vcf_reader = vcf.Reader(open(self.raw_data_file_path), 'r')
		for record in vcf_reader:
			if record.ID in SNPs_to_look_for:
				call = record.genotype(vcf_reader.samples[0])
				bases = call.gt_bases[0] + call.gt_bases[2]  #just save GG, not something like G/G
				self.SNP_calls[record.ID] = bases

	def write_session_data_file(self):
		"""Pickle the SNP_calls dict to a file."""
		with open(self.session_data_file_path, 'w') as handle:
			pickle.dump(self.SNP_calls, handle)	