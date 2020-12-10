from django.apps import AppConfig


class CuratedCategoriesConfig(AppConfig):
    name = 'curated_categories'

    def ready(self):
        from curated_categories.models import CuratedCategory

        CATEGORIES = (
            ('app_type', 'IGB_Plug_in', 'How an App changes the IGB interface',
             'Plugin Apps add new menus to the IGB interface'),

            ('app_type', 'Application', 'How an App changes the IGB interface',
             'Application Apps add new windows to the IGB Interface'),

            ('biology', 'Microbial_Genomics', 'Apps categorized by biological research area',
             'Apps for analysis and visualization of microbial genomic data'),

            ('biology', 'Plant_Genomics', 'Apps categorized by biological research area',
             'Apps for analysis and visualization of genomes from photosynthetic organisms'),

            ('biology', 'Protein', 'Apps categorized by biological research area',
             'Apps for searching or visualizing of protein structure or function'),

            ('biology', 'Epigenome', 'Apps categorized by biological research area',
             'Apps for visualizing or searching DNA or histone modification diversity'),

            ('biology', 'Alternative_Splicing', 'Apps categorized by biological research area',
             'Apps that show splicing pattern diversity'),

            ('biology', 'Transcriptome', 'Apps categorized by biological research area',
             'Apps that display RNA expression data'),

            ('data', 'ChIP-Seq', 'Apps categorized by data formats and data types',
             'Apps that display DNA sequenced from chromatin precipitation experiments'),

            ('data', 'RNA-Seq', 'Apps categorized by data formats and data types',
             'Apps that display RNA sequence alignments, coverage graphs, and related data'),

            ('data', 'Bisulfite', 'Apps categorized by data formats and data types',
             ' Apps that display DNA from bisulfite sequencing to detect DNA methylation'),

            ('data', 'DNA-Seq', 'Apps categorized by data formats and data types',
             'Apps that display genomic DNA sequencing results'),
        )
        try:
            for type, subcat, type_desc, cat_desc in CATEGORIES:
                curated_cat, _ = CuratedCategory.objects.get_or_create(curated_category_type=type,
                                                                       curated_category=subcat,
                                                                       type_description=type_desc,
                                                                       curated_category_description=cat_desc)
        except:
            pass