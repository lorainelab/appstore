from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import AppPending

def app_pending_cleanup():
    pending_objs = AppPending.objects.filter(submitter_approved=False)
    for pending_obj in pending_objs:
        pending_obj.delete_files()
        pending_obj.delete()

def start():
    scheduler = BackgroundScheduler()
    #call function 'app_pending_cleanup' everyday at midnight
    scheduler.add_job(app_pending_cleanup, CronTrigger.from_crontab('* * * * *'))
    scheduler.start()