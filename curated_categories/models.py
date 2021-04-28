from django.db import models
from apps.models import App


class CuratedCategory(models.Model):
    CATEGORIES = (
        ('app_type', 'App Type'),
        ('biology', 'Biology'),
        ('data', 'Data'),
    )

    curated_category_type   = models.CharField(max_length=255, choices=CATEGORIES)
    type_description        = models.CharField(max_length=500, blank=True)
    curated_category        = models.CharField(max_length=255, unique=True)
    curated_category_description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.curated_category

    @property
    def count(self):
        return CuratedCategoriesMapping.objects.filter(curated_categories=self).count()

    class Meta:
        ordering = ["curated_category_type"]
        verbose_name_plural = "curated_categories"


class CuratedCategoriesMapping(models.Model):

    curated_categories = models.ManyToManyField(CuratedCategory, blank=True)
    app = models.ForeignKey(App, blank=False, on_delete=models.CASCADE)

    class Meta:
        ordering = ["app"]
        verbose_name_plural = "curated_categories_mapping"
