from django.contrib import admin
from SNP_Feature_View.models import Phenotype, Pheno_Geno_Morphology, SNP, SampleFile


class PhenoGenoMorphologyInline(admin.TabularInline):
	model = Pheno_Geno_Morphology
	extra = 3


class PhenotypeAdmin(admin.ModelAdmin):
	inlines = [PhenoGenoMorphologyInline]


class SampleFileAdmin(admin.ModelAdmin):
	list_display = ('url', 'file_type', 'readable_size')


class SNPAdmin(admin.ModelAdmin):
	list_display = ('SNP_ID', 'chromosome_num', 'chromosome_pos_GRCh37', 'associated_phenotype')

admin.site.register(Phenotype, PhenotypeAdmin)
admin.site.register(SNP, SNPAdmin)
admin.site.register(SampleFile, SampleFileAdmin)
