from django.core.management.base import BaseCommand, CommandError
from SNP_Feature_View.models import SNP

import os
import sys

class Command(BaseCommand):
    help = 'Create a BED file with all the SNPs from our SNP database.'

    def handle(self, *args, **options):
		self.stdout.write('Writing SNPs into BED file...')
		b = BEDFileGenerator()
		b.write_BED_file()


class BEDFileGenerator():
	def __init__(self):
		self.file_dir = 'media/SNP_Feature_View/JBrowse/BED_files/'
		self.file_name = 'SNP_BED_file.bed'
		self.file_path = self.file_dir + self.file_name

	def write_BED_file(self):
		"""Write a bed line for every SNP in database."""
		all_SNPs = SNP.objects.all()
		with open(self.file_path, 'w') as handle:
			for s in all_SNPs:
				chrom_num = str(s.chromosome_num)
				chrom_pos = str(s.chromosome_pos_GRCh37)
				BED_line = chrom_num + "\t" + chrom_pos + "\t" + chrom_pos + "\t" + s.SNP_ID + "\n"
				handle.write(BED_line)