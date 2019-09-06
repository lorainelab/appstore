import re
import hashlib
from shutil import rmtree
import subprocess
from os import mkdir, devnull
import os.path
from os.path import join as pathjoin
from urllib.parse import urljoin
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse

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

_TagCountCache = dict()

class Tag(models.Model):
	name     = models.CharField(max_length=255, unique=True)
	fullname = models.CharField(max_length=255)

	@property
	def count(self):
		global _TagCountCache
		if self.name in _TagCountCache:
			count = _TagCountCache[self.name]
		else:
			count = App.objects.filter(active = True, tags = self).count()
			_TagCountCache[self.name] = count
		return count

	search_schema = ('fullname', )
	search_key = 'name'

	def __unicode__(self):
		return self.name
	class Meta:
		ordering = ["name"]

GENERIC_ICON_URL = urljoin(settings.STATIC_URL, 'apps/img/app_icon_generic.png')

def app_icon_path(app, filename):
    return filename

class App(models.Model):
    name         = models.CharField(max_length=127, unique=True)
    fullname     = models.CharField(max_length=127, unique=True)
    symbolicname = models.CharField(max_length=127, unique=True)
    description  = models.CharField(max_length=255, blank=True, null=True)
    details      = models.TextField(blank=True, null=True)
    version       = models.TextField(blank=False)
    tags         = models.ManyToManyField(Tag, blank=True)

    icon         = models.ImageField(blank=True, null=True)

    authors      = models.ManyToManyField(Author, blank=True, through='OrderedAuthor')
    editors      = models.ManyToManyField(User, blank=True)

    latest_release_date       = models.DateField(blank=True, null=True)
    has_releases              = models.BooleanField(default=False)
    release_file    = models.FileField()
    release_file_name = models.CharField(max_length=127)
    license_text    = models.URLField(blank=True, null=True)
    license_confirm = models.BooleanField(default=False)

    website      = models.URLField(blank=True, null=True)
    tutorial     = models.URLField(blank=True, null=True)
    citation     = models.CharField(max_length=31, blank=True, null=True)
    coderepo     = models.URLField(blank=True, null=True)

    contact      = models.EmailField(blank=True, null=True)

    stars        = models.PositiveIntegerField(default=0)
    downloads    = models.PositiveIntegerField(default=0)

    repository = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)

    def is_editor(self, user):
        if not user:
            return False
        if user.is_staff or user.is_superuser:
            return True
        return user in self.editors.all()

    def __str__(self):
        return self.fullname

    @property
    def stars_percentage(self):
        return 100 * self.stars / 5

    @property
    def icon_url(self):
        return self.icon.url if self.icon else GENERIC_ICON_URL

    @property
    def releases(self):
        return self.release_set.filter(active=True).all()

    def update_has_releases(self):
        self.has_releases = (self.release_set.filter(active=True).count() > 0)
        self.save()
        self.delete_releases()

    def delete_releases(self):
        if not self.has_releases:
            self.release_file.delete()
            self.delete()

    @property
    def page_url(self):
        return reverse('app_page', args=[self.name])

    @property
    def ordered_authors(self):
        return (a.author for a in OrderedAuthor.objects.filter(app = self))

    search_schema = ('^fullname', 'description', 'details')
    search_key = 'name'

    def __unicode__(self):
        return self.name

@receiver(models.signals.pre_delete, sender=App)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes Release files on `post_delete` """
    if instance.release_file:
        instance.release_file.delete()

class OrderedAuthor(models.Model):
    author       = models.ForeignKey(Author,on_delete=models.CASCADE)
    app          = models.ForeignKey(App,on_delete=models.CASCADE)
    author_order = models.PositiveSmallIntegerField(default = 0)

    def __unicode__(self):
        return unicode(self.author_order) + ': ' + self.app.name + ' by ' + self.author.name

    class Meta:
        ordering = ["author_order"]

VersionRE = re.compile(r'^(\d+)(?:\.(\d)+)?(?:\.(\d)+)?(?:\.([\w-]+))?$')

def release_file_path(release, filename):
    return pathjoin(release.app.name, 'releases', release.version, filename)

class Release(models.Model):
    app           = models.ForeignKey(App,on_delete=models.CASCADE)
    version       = models.CharField(max_length=31)
    works_with    = models.CharField(max_length=31)
    notes         = models.TextField(blank=True, null=True)
    created       = models.DateTimeField(auto_now_add=True)
    active        = models.BooleanField(default=True)

    repository    = models.TextField(blank=True, null=True)
    release_file  = models.FileField(upload_to=release_file_path)
    release_file_name = models.CharField(max_length=127)
    hexchecksum   = models.CharField(max_length=511, blank=True, null=True)

    @property
    def version_tuple(self):
        matched = VersionRE.match(self.version)
        if not matched:
            return None
        (major, minor, patch, tag) = matched.groups()
        major = int(major)
        minor = int(minor) if minor else None
        patch = int(patch) if patch else None
        return (major, minor, patch, tag)

    @property
    def created_iso(self):
        return self.created

    @property
    def release_file_url(self):
        return self.release_file.url if self.release_file else None

    @property
    def release_download_url(self):
        return reverse('release_download', args=[self.app.name, self.version])

    def __unicode__(self):
        return self.app.fullname + ' ' + self.version

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
        if self.releaseapi_set.count() > 0:
            api = self.releaseapi_set.get()
            api.delete_files()
            api.delete()

    class Meta:
        ordering = ['-created']

def screenshot_path(screenshot, filename):
    return pathjoin(screenshot.app.name, 'screenshots', filename)

def thumbnail_path(screenshot, filename):
    return pathjoin(screenshot.app.name, 'thumbnails', filename)

class Screenshot(models.Model):
    app        = models.ForeignKey(App,on_delete=models.CASCADE)
    screenshot = models.ImageField(upload_to=screenshot_path)
    thumbnail  = models.ImageField(upload_to=thumbnail_path)

    def __unicode__(self):
        return '%s - %d' % (self.app.fullname, self.id)
