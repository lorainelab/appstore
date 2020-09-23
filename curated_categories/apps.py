from django.apps import AppConfig


class CuratedCategoriesConfig(AppConfig):
    name = 'curated_categories'

    def ready(self):
        from curated_categories.models import CuratedCategory

        CATEGORIES = (
            ('app_type', 'IGB_Plug_in'),
            ('app_type', 'Application'),
            ('biology', 'Transcriptome'),
            ('biology', 'Epigenome'),
            ('biology', 'Alternative_Splicing'),
            ('data', 'ChIP-Seq'),
            ('data', 'RNA-Seq'),
            ('data', 'Bisulfite'),
            ('data', 'DNA-Seq'),
        )
        try:
            for type, subcat in CATEGORIES:
                curated_cat, _ = CuratedCategory.objects.get_or_create(curated_category_type=type, curated_category=subcat)
        except:
            pass