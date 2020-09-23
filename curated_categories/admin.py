from django.contrib import admin
from curated_categories.models import CuratedCategory, CuratedCategoriesMapping

admin.site.register(CuratedCategory)
admin.site.register(CuratedCategoriesMapping)
