import hashlib
import re
from os.path import join as pathjoin
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.urls import reverse


class Category(models.Model):
    name     = models.CharField(max_length=255, unique=True)
    fullname = models.CharField(max_length=255)

    @property
    def count(self):
        return App.objects.filter(categories = self).count()

    search_schema = ('fullname', )
    search_key = 'name'

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"


class App(models.Model):
    Bundle_Name         = models.CharField(max_length=127, unique=True)
    Bundle_SymbolicName = models.CharField(max_length=127, unique=True)

    categories          = models.ManyToManyField(Category, blank=True)
    editors             = models.ManyToManyField(User, blank=True)

    stars               = models.PositiveIntegerField(default=0)

    def is_editor(self, user):
        if not user:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return user in self.editors.all()

    def __str__(self):
        return self.Bundle_Name

    @property
    def stars_percentage(self):
        return 100 * self.stars / 5

    @property
    def page_url(self):
        return reverse('app_page', args=[self.Bundle_SymbolicName])

    search_schema = ('^Bundle_Name')
    search_key = 'name'

    def __unicode__(self):
        return self.Bundle_Name


@receiver(models.signals.pre_delete, sender=App)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes Release files on `post_delete` """
    if instance.release_file:
        instance.release_file.delete()
    if instance.logo:
        instance.logo.delete()


class Author(models.Model):
    name        = models.CharField(max_length=255)
    institution = models.CharField(max_length=255, null=True, blank=True)

    search_schema = ('name', 'institution')
    search_key = 'id'

    def __unicode__(self):
        if not self.institution:
            return self.name
        else:
            return self.name + ' (' + self.institution + ')'


VersionRE = re.compile(r'^(\d+)(?:\.(\d)+)?(?:\.(\d)+)?(?:\.([\w-]+))?$')


def release_file_path(release, filename):
    return pathjoin(release.app.Bundle_SymbolicName, 'releases', release.Bundle_Version, release.app.Bundle_SymbolicName + '-' +
                    release.Bundle_Version + '.jar')


def logo_path(release, filename):
    get_ext = filename.split('.')[-1]
    return pathjoin(release.app.Bundle_SymbolicName, 'releases', release.Bundle_Version, release.app.Bundle_SymbolicName + '-' +
                    release.Bundle_Version + '.' + get_ext)


GENERIC_LOGO_URL = urljoin(settings.STATIC_URL, 'apps/img/app_icon_generic.png')


class Release(models.Model):
    app                     = models.ForeignKey(App, on_delete=models.CASCADE)
    Bundle_Version          = models.CharField(max_length=31)
    short_title             = models.CharField(max_length=255, blank=True, null=True)
    Bundle_Description      = models.TextField(blank=True, null=True)

    license_url             = models.URLField(blank=True, null=True)
    license_confirm         = models.BooleanField(default=False)

    website_url             = models.URLField(blank=True, null=True)
    tutorial_url            = models.URLField(blank=True, null=True)
    citation                = models.CharField(max_length=31, blank=True, null=True)
    code_repository_url     = models.URLField(blank=True, null=True)

    contact_email           = models.EmailField(blank=True, null=True)

    platform_compatibility  = models.CharField(max_length=31)
    created                 = models.DateTimeField(auto_now_add=True)
    active                  = models.BooleanField(default=True)
    logo                    = models.ImageField(blank=True, null=True, upload_to=logo_path)

    repository_xml          = models.TextField(blank=True, null=True)  # OBR Index Repository XML
    release_file            = models.FileField(upload_to=release_file_path)

    hexchecksum             = models.CharField(max_length=511, blank=True, null=True)

    stars = models.PositiveIntegerField(default=0)

    uploader_ip = models.GenericIPAddressField(null=True)

    authors                 = models.ManyToManyField(Author, blank=True, through='OrderedAuthor')

    # To Display Release App and its version on Admin Panel > Releases Tab
    def __str__(self):
        return self.app.Bundle_Name + " - " +  self.Bundle_Version

    @property
    def ordered_authors(self):
        return (a.author for a in OrderedAuthor.objects.filter(release=self))

    @property
    def version_tuple(self):
        matched = VersionRE.match(self.Bundle_Version)
        if not matched:
            return None
        (major, minor, patch, tag) = matched.groups()
        major = int(major)
        minor = int(minor) if minor else None
        patch = int(patch) if patch else None
        return major, minor, patch, tag

    @property
    def created_iso(self):
        return self.created

    @property
    def release_file_url(self):
        return self.release_file.url if self.release_file else None

    @property
    def release_download_url(self):
        return reverse('release_download', args=[self.app.Bundle_SymbolicName, self.Bundle_Version])

    @property
    def logo_url(self):
        return self.logo.url if self.logo else GENERIC_LOGO_URL

    def __unicode__(self):
        return self.app.Bundle_Name + ' ' + self.Bundle_Version

    def calc_checksum(self):
        cs = hashlib.sha512()
        f = self.release_file.file
        f.open('rb')
        while True:
            buf = f.read(128)
            if not buf: break
            cs.update(buf)
        f.close()
        self.hexchecksum = '%s:%s' % (cs.name, cs.hexdigest())
        self.save()

    def delete_files(self):
        self.release_file.delete()

    def delete_logo(self):
        self.logo.delete()

    class Meta:
        ordering = ['-created']

    search_schema = ('^Bundle_Name', 'short_title', 'Bundle_Description')
    search_key = 'name'


def screenshot_path(screenshot, filename):
    get_ext = filename.split('.')[-1]
    return pathjoin(screenshot.release.app.Bundle_SymbolicName, 'releases', screenshot.release.Bundle_Version, 'screenshots',
                    filename + '_' +screenshot.release.app.Bundle_SymbolicName + '-' + screenshot.release.Bundle_Version + '.' + get_ext)


def thumbnail_path(screenshot, filename):
    get_ext = filename.split('.')[-1]
    return pathjoin(screenshot.release.app.Bundle_SymbolicName, 'releases', screenshot.release.Bundle_Version, 'thumbnails',
                    filename + '_' +screenshot.release.app.Bundle_SymbolicName + '-' + screenshot.release.Bundle_Version + '.' + get_ext)


class Screenshot(models.Model):
    release        = models.ForeignKey(Release, on_delete=models.CASCADE)
    screenshot = models.ImageField(upload_to=screenshot_path)
    thumbnail  = models.ImageField(upload_to=thumbnail_path)

    def __unicode__(self):
        return '%s - %d' % (self.app.Bundle_Name, self.id)


@receiver(models.signals.pre_delete, sender=Release)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes Release files on `post_delete` """
    if instance.release_file:
        instance.release_file.delete()
    if instance.logo:
        instance.logo.delete()


class OrderedAuthor(models.Model):
    author       = models.ForeignKey(Author, on_delete=models.CASCADE)
    release          = models.ForeignKey(Release, on_delete=models.CASCADE)
    author_order = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return unicode(self.author_order) + ': ' + self.app.Bundle_Name + ' by ' + self.author.name

    class Meta:
        ordering = ["author_order"]
