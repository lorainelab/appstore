import datetime
from os.path import basename

from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver

from apps.models import App, Release
from util.id_util import fullname_to_name
from util.view_util import get_object_or_none

try:
    from conf.emails import EMAIL_ADDR
except ImportError:
    from conf.mock import EMAIL_ADDR


class AppPending(models.Model):
    submitter           = models.ForeignKey(User,on_delete=models.CASCADE)
    bundle_name            = models.CharField(max_length=127) # Bundle-Name
    symbolicname        = models.CharField(max_length=127) # Bundle-SymbolicName
    details             = models.TextField(blank=True, null=True) # Bundle-Description
    version             = models.CharField(max_length=31) # Bundle-Version
    works_with          = models.CharField(max_length=31, null=True, blank=True, default="9.1.0")
    created             = models.DateTimeField(auto_now_add=True)
    repository          = models.TextField(blank=True, null=True) # OBR index file repository.xml
    release_file_name = models.CharField(max_length=127) # ?
    release_file        = models.FileField(upload_to='pending_releases') # ?

    def __str__(self):
        return self.bundle_name

    def can_confirm(self, user):
        if user.is_staff or user.is_superuser:
            return True
        return user.username == self.submitter.username

    @property
    def is_new_app(self):
        name = fullname_to_name(self.bundle_name)
        return get_object_or_none(App, name = name) == None

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.bundle_name + ' ' + self.version + ' from ' + self.submitter.email

    def make_release(self, app):
        release, _ = Release.objects.get_or_create(app=app, version=self.version)
        release.works_with = self.works_with
        release.active = True
        release.created = datetime.datetime.today()
        release.repository = self.repository
        release.save()
        release.release_file.save(basename(self.release_file.name), self.release_file)
        app.release_file.save(release.release_file.name, release.release_file)
        app.release_file_name = basename(app.release_file.name)
        app.save()
        if not app.has_releases:
            app.has_releases = True
        app.latest_release_date = release.created
        app.save()

    def delete_files(self):
        self.release_file.delete()

@receiver(models.signals.pre_delete, sender=AppPending)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes Jar from Pending Releases folder in S3 on `post_delete` """
    if instance.release_file:
        instance.release_file.delete()
