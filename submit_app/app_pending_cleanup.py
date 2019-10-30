from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from util.view_util import get_object_or_none
from .models import AppPending

def app_pending_cleanup():
    not_submitter_approved_objs = AppPending.objects.filter(submitter_approved=False)
    for not_submitter_approved_obj in not_submitter_approved_objs:
        submitter_approved_obj = get_object_or_none(AppPending, Bundle_SymbolicName=not_submitter_approved_obj.Bundle_SymbolicName, submitter_approved=True)
        if(submitter_approved_obj):
            # to prevent deletion of s3 jar file as the app is approved by the submitter
            not_submitter_approved_obj.release_file=""
        not_submitter_approved_obj.delete()

def start():
    scheduler = BackgroundScheduler()
    # call function 'app_pending_cleanup' everyday at midnight
    scheduler.add_job(app_pending_cleanup, CronTrigger.from_crontab('0 0 * * *'))
    scheduler.start()