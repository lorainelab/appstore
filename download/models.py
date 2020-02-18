from django.db import models
from django.db.models import Model, CharField, PositiveIntegerField, ForeignKey, DateField
from apps.models import App, Release
from util.view_util import ipaddr_long_to_str


class Download(Model):
    release = ForeignKey(Release, related_name='app_download_stats',on_delete=models.CASCADE)
    when    = DateField()
    ip4addr = PositiveIntegerField()

    def __unicode__(self):
        return unicode(self.release) + u' ' + unicode(self.when) + u' ' + ipaddr_long_to_str(self.ip4addr)


class ReleaseDownloadsByDate(Model):
    release = ForeignKey(Release, null = True, on_delete=models.CASCADE) # null release has total count across a given day
    when    = DateField()
    count   = PositiveIntegerField(default = 0, null = False, blank = False)

    def __unicode__(self):
        return unicode(self.release) + u' ' + unicode(self.when) + u': ' + unicode(self.count)
