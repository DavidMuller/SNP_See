Motivation
=======
Project motivation can be found in the following paper: 


Project Dependencies
=======
Built with Django 1.6.5

Dependencies:

<a href="http://pyvcf.readthedocs.org/en/latest/">PyVCF</a> for parsing VCF files.  PyVCF can be installed with: `pip install pyvcf`

Biopython: `sudo apt-get install python-biopython`


JBrowse
=======
We used JBrowse 1.11.4 in this project: http://jbrowse.org/

We seeded JBrowse with the (1) GRCh37 human reference sequece, (2) RefSeq genes, and (3) Common SNPs(138).  We've uploaded the source data for those 3 tracks for convenience (fasta files for the reference genomes, BED files for the RefSeq genes and Common SNPs(138)): https://drive.google.com/folderview?id=0B_Z3ZgWqIL8nQld0ZjE4WTRQLW8&usp=sharing

All data was originally downloaded from UCSC--we used the table browser for the RefSeq Genes and Common SNPs(138): http://genome.ucsc.edu/cgi-bin/hgTables?org=human


The source tracks were formatted for use in JBrowse, with JBrowse's `bin/prepare-refseqs.pl` (for the GRCh37 reference sequence), and `bin/flatfile-to-json.pl` for the RefSeq genes and common SNPs.  


The JBrowse 1.11.4 folder normally lives in the 'static' folder in the root directory of this repository (next to Bootstrap, and JQuery).  


'Sample Genetic Data' 
=======
All of the genetic information we used as sample genetic files were downloaded from the personal genome project: https://my.pgp-hms.org/public_genetic_data

The sample genetic files we use normally reside in the 'media' folder at the root level of the repository.  The 'media' folder was not committed to GitHub (it's large), but is hosted here: https://drive.google.com/folderview?id=0B_Z3ZgWqIL8nMVNHdjhLcmZ6WFk&usp=sharing

The sample genetic files are in `media/SNP_Feature_View/sample_files`


Django management Scripts
=======
We've written 2 management scripts: generate_session_data, and create_SNP_BED_file

generate_session_data is invoked with Django as follows: `python manage.py generate_session_data`

It takes all sample files contained in the Django backing database and searches them for SNP calls that SNP See uses to determine traits.  SNP calls contained in the sample file, and used by SNP See, are added to a dictionary and pickled out to a file in `media/SNP_Feature_View/sample_files_as_session_data`

create_SNP_BED_file is invoked with Django as follows: `python create_SNP_BED_file`

It takes the SNP relation maintained by Django, and writes it to a BED file--specifically it writes the file `media/SNP_Feature_View/JBrowse/BED_files/SNP_BED_file.bed`  (That BED file can be incorporated into JBrowse for viewing using JBrowse's bin/flatfile-to-json.pl script.)  
