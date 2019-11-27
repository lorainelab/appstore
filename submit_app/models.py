import copy
import datetime
from os.path import basename

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from apps.models import App, Release
from util.view_util import get_object_or_none

try:
    from conf.emails import EMAIL_ADDR
except ImportError:
    from conf.mock import EMAIL_ADDR


class AppPending(models.Model):
    submitter           = models.ForeignKey(User,on_delete=models.CASCADE)
    Bundle_Name         = models.CharField(max_length=127)  # Bundle-Name
    Bundle_SymbolicName = models.CharField(max_length=127) # Bundle-SymbolicName
    Bundle_Description  = models.TextField(blank=True, null=True) # Bundle-Description
    Bundle_Version      = models.CharField(max_length=31) # Bundle-Version
    works_with          = models.CharField(max_length=31, null=True, blank=True)
    created             = models.DateTimeField(auto_now_add=True)
    updated             = models.DateTimeField(auto_now=True)
    repository_xml      = models.TextField(blank=True, null=True) # OBR index file repository.xml
    release_file_name   = models.CharField(max_length=127) # ?
    release_file        = models.FileField(upload_to='pending_releases') # ?
    submitter_approved  = models.BooleanField(default=False)
    uploader_ip         = models.GenericIPAddressField(null=True)


    def __str__(self):
        return self.Bundle_Name

    def can_confirm(self, user):
        if user.is_staff or user.is_superuser:
            return True
        return user.username == self.submitter.username

    @property
    def is_new_app(self):
        return get_object_or_none(App, Bundle_SymbolicName = self.Bundle_SymbolicName) == None

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.Bundle_Name + ' ' + self.Bundle_Version + ' from ' + self.submitter.email

    def make_release(self, app):
        # copy fields from previous released app into new release of same app
        previous_release = copy.copy(Release.objects.filter(app=app).order_by('-Bundle_Version')[:1])
        release, _ = Release.objects.get_or_create(app=app, Bundle_Version=self.Bundle_Version)
        release.platform_compatibility = self.works_with
        release.created = datetime.datetime.today()
        release.Bundle_Description = self.Bundle_Description
        release.repository_xml = self.repository_xml
        release.uploader_ip = self.uploader_ip
        release.save()
        release.release_file.save(basename(self.release_file.name), self.release_file)
        release.calc_checksum()
        if previous_release:
            release.short_title = previous_release[0].short_title
            release.license_url = previous_release[0].license_url
            release.license_confirm = previous_release[0].license_confirm
            release.website_url = previous_release[0].website_url
            release.tutorial_url = previous_release[0].tutorial_url
            release.citation = previous_release[0].citation
            release.code_repository_url = previous_release[0].code_repository_url
            release.contact_email = previous_release[0].contact_email
            if previous_release[0].logo:
                release.logo.save(previous_release[0].logo.name, previous_release[0].logo)
            for author in previous_release[0].authors.all():
                release.authors.add(author)
        release.save()
        return release

    def delete_files(self):
        self.release_file.delete()

@receiver(models.signals.pre_delete, sender=AppPending)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes Jar from Pending Releases folder in S3 on `post_delete` """
    if instance.release_file:
        instance.release_file.delete()
