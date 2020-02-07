import base64
import re
import os
from os.path import basename
from platform import release
from urllib.request import urlopen
from zipfile import ZipFile

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse

from apps.models import Release, App, Author, OrderedAuthor
from util.id_util import fullname_to_name
from util.view_util import html_response, json_response, get_object_or_none
from .models import AppPending
from .processjar import process_jar
from xml.etree import ElementTree as ET

# IGBF-2026 start
APP_REPLACEMENT_JAR_MSG = "This is a <b>replacement jar file</b> for a not yet released App that you or a colleague already uploaded previously but is still in our “pending apps” waiting area. If you choose to submit it, this new jar file will replace the one that was uploaded before."
NEW_VERSION_APP_MSG = "This is a <b>new version of a released App.</b> If you choose to submit it, your new version will appear right away in the App Store."
ALL_NEW_APP_MSG = "This is an <b>all-new App.</b> No released or pending App in App Store has the same Bundle_SymbolicName. Congratulations on your App’s first release!"
ALREADY_RELEASED_APP_MSG = "Bundle_Version and Bundle_SymbolicName match an <b>already-released App.</b> We are sorry – this is not allowed! If you want users to get the new version, you must increase Bundle_Version. For example, if the released version is 1.0.0, the new version should be 1.0.1 or higher."
NOT_YET_RELEASED_APP_MSG = "The jar file Bundle_SymbolicName matches a previously uploaded but <b>not yet released App.</b> The previously uploaded App’s Bundle_Version is different, however. Are you trying to release different versions of the same App. No problem!"
# IGBF-2026 end

# Presents an app submission form and accepts app submissions.
@login_required
def submit_app(request):
    context = dict()
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
        request.META['REMOTE_ADDR'] = ip
    client_ip = request.META['REMOTE_ADDR']
    if request.method == 'POST':
        expect_app_name = request.POST.get('expect_app_name')
        f = request.FILES.get('file')
        f = request.POST.get('url_val', None) if f is None else f
        if f:
            try:
                jar_details = process_jar(f, expect_app_name)
                pending = _create_pending(request.user, jar_details, f, client_ip)
                version_pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
                version_pattern = re.compile(version_pattern)
                if not bool(version_pattern.match(jar_details['Bundle_Version'])):
                    raise ValueError("Bundle-Version %s is incorrect. Please use semantic versioning. " 
                                                                                        "See https://semver.org/." %jar_details['Bundle_Version'])
                return HttpResponseRedirect(reverse('confirm-submission', args=[pending.id]))
            except ValueError as e:
                context['error_msg'] = str(e)
    else:
        expect_app_name = request.GET.get('expect_app_name')
        if expect_app_name:
            context['expect_app_name'] = expect_app_name
    return html_response('upload_form.html', context, request)


def _user_cancelled(request, pending):
    pending.delete_files()
    pending.delete()
    return HttpResponseRedirect(reverse('submit-app'))


def _user_accepted(request, pending):
    app = get_object_or_none(App, Bundle_SymbolicName = pending.Bundle_SymbolicName)
    if app:
        if not app.is_editor(request.user):
            return HttpResponseForbidden('You are not authorized to add releases, because you are not an editor')
        release = pending.make_release(app)
        pending.delete_files()
        pending.delete()
        return html_response('update_apps.html', {'Bundle_SymbolicName': app.Bundle_SymbolicName,
                                                  'Bundle_Name': app.Bundle_Name,
                                                  'Bundle_Version': release.Bundle_Version}, request)
        #return HttpResponseRedirect(reverse('app_page_edit', args=[app.Bundle_SymbolicName]) + '?upload_release=true') # For Future Reference
    else:
        pending.submitter_approved = True
        pending.save()
        return html_response('submit_done.html', {'app_name': pending.Bundle_Name}, request)


def confirm_submission(request, id):
    context = dict()
    pending = get_object_or_none(AppPending, id=int(id) )
    if pending is None:
        context['error_msg'] = str("Sorry, this App is not longer in our system because too much time has passed since "
                                   "you first uploaded it. No problem! Please try again.")
        return html_response('upload_form.html', context, request)
    
    if not pending.can_confirm(request.user):
        return HttpResponseRedirect('/')
    pending_obj = AppPending.objects.filter(Bundle_SymbolicName=pending.Bundle_SymbolicName, Bundle_Version=pending.Bundle_Version)
    is_pending_replace = True if pending_obj.count() > 1 else False
    # IGBF-2026 start
    app_summary, is_app_submission_error = _app_summary(pending)
    if is_app_submission_error:
        return html_response('error.html', {'pending': pending, 'app_summary': app_summary}, request)
    # IGBF-2026 end
    error_message = "Please note: We read your App's repository.xml file but could not determine the IGB version it requires. Not to worry! You can enter this information manually after the App is released." \
        if pending.works_with is None else None
    action = request.POST.get('action')
    if action:
        latest_pending_obj_ = pending_obj[1] if is_pending_replace else pending_obj[0]
        if action == 'cancel':
            return _user_cancelled(request, latest_pending_obj_)
        elif action == 'accept':
            if pending_obj.count() > 1:
                _replace_jar_details(request, pending_obj)
            server_url = _get_server_url(request)
            _send_email_for_pending(server_url, latest_pending_obj_)
            _send_email_for_pending_user(latest_pending_obj_)
            return _user_accepted(request, latest_pending_obj_)
    return html_response('confirm.html',{'pending': pending, 'app_summary': app_summary, 'info_msg': error_message}, request)


# Get the Current Directory Path to Temporarily store the Zip File
dir_path = os.path.dirname(os.path.abspath(__file__))


# IGBF-2026 start
def _app_summary(pending):

    is_app_submission_error = False
    app_summary = ALL_NEW_APP_MSG
    is_app_status_set = False
    pending_obj = get_object_or_none(AppPending, Bundle_SymbolicName=pending.Bundle_SymbolicName, submitter_approved=True)
    app = get_object_or_none(App, Bundle_SymbolicName=pending.Bundle_SymbolicName)
    if app is not None:
        released_objs = Release.objects.filter(active=True, app=app)
        for released_obj in released_objs:
            if released_obj.Bundle_Version == pending.Bundle_Version:
                is_app_submission_error = True
                is_app_status_set = True
                app_summary = ALREADY_RELEASED_APP_MSG
                break
        if (not is_app_status_set):
            app_summary = NEW_VERSION_APP_MSG
    if (pending_obj):
        if pending_obj.Bundle_Version == pending.Bundle_Version:
            app_summary = APP_REPLACEMENT_JAR_MSG
            is_app_status_set = True
        if(not is_app_status_set):
            app_summary = NOT_YET_RELEASED_APP_MSG

    return app_summary, is_app_submission_error
# IGBF-2026 end


def _create_pending(submitter, jar_details, release_file, client_ip):

    # Todo : Add the required IGB packages
    regex = r'org.lorainelab.igb|com.affymetrix'
    repo_tree = ET.fromstring(jar_details['repository'])
    version_list = []
    for require in repo_tree.find('resource').findall('require'):
        if re.search(regex, require.text) is not None:
            version = re.findall(r'\[.*?\)|\[.*?\]|\(.*?\)|\(.*?\]|\d+.?\d+.?\d+|\d+', require.text)
            if len(version) > 0:
                version_list.append(version[0])

    if version_list is None or len(version_list) <= 0:
        frequest_used_version_ = None
    else:
        # Todo : Post a warning if the versions of all IGB packages are not matching
        frequest_used_version_ = max(set(version_list), key=version_list.count)
        frequest_used_version_ = frequest_used_version_ if (frequest_used_version_.startswith(("(", "["))) else frequest_used_version_ + "+"

    pending, created = AppPending.objects.update_or_create(submitter       = submitter,
                                        Bundle_SymbolicName    = jar_details['Bundle_SymbolicName'],
                                        Bundle_Description     = base64.b64decode(jar_details['Bundle_Description']).decode('utf-8'),
                                        Bundle_Name        = jar_details['Bundle_Name'],
                                        Bundle_Version         = jar_details['Bundle_Version'],
                                        repository_xml      = jar_details['repository'],
                                        submitter_approved = False,
                                        uploader_ip = client_ip,
                                        works_with=frequest_used_version_)
    file, file_name = _get_jar_file(release_file)
    pending.release_file.save(basename(file_name), file)
    pending.release_file_name = file_name
    pending.logo = ""
    pending.save()
    if isinstance(release_file, str):
        os.remove(dir_path + file_name)
    return pending


def _replace_jar_details(request, pending_obj):
    """
    The function replaces the existing pending app details with the latest jar details
    if the jar is not yet released else replaces the released app details with the latest
    app details.
    :param request:
    :param pending_obj:
    :return:
    """
    latest_pending_obj = pending_obj[pending_obj.count() - 1]
    existing_pending_obj = pending_obj[pending_obj.count() - 2]
    if latest_pending_obj and latest_pending_obj.submitter != request.user:
        raise ValueError('cannot be accepted because you are not an editor')
    existing_pending_obj.release_file = ""
    existing_pending_obj.delete()
    latest_pending_obj.save()


def _get_jar_file(release_file):
    """
    The function checks if the given file is a url. If yes, it reads the
    details into a temporary file and returns
    the file object and file name else returns the given file object.
    :param release_file:
    :return:
    """
    file_name = basename(release_file) if isinstance(release_file, str) else basename(release_file.name)
    if isinstance(release_file, str):
        url_data = urlopen(release_file).read()
        with open(dir_path + file_name, 'wb') as file:
            file.write(url_data)
        file = open(dir_path + file_name, 'rb')
    else:
        file = release_file
    return file, file_name


def _send_email_for_pending(server_url, pending):
    admin_url = reverse('admin:login', current_app=pending.Bundle_SymbolicName)
    msg = u"""
The following app has been submitted:
    ID: {id}
    Name: {Bundle_Name}
    Version: {version}
    Submitter: {submitter_name} {submitter_email}
    Server Url: {server_url}{admin_url}
""".format(id=pending.id, Bundle_Name=pending.Bundle_Name, version=pending.Bundle_Version, submitter_name=pending.submitter.username, submitter_email=pending.submitter.email, server_url=server_url, admin_url=admin_url)
    send_mail('{Bundle_Name} App - Successfully Submitted.'.format(Bundle_Name=pending.Bundle_Name), msg, settings.EMAIL_ADDR, settings.CONTACT_EMAILS, fail_silently=False)


def _send_email_for_pending_user(pending):
    msg = u"""
Thank you for submitting the app! {approve_text}
The following app has been submitted:
    Name: {Bundle_Name}
    Version: {version}
    Submitter: {submitter_name} {submitter_email}
""".format(approve_text="You'll be notified by email when your app has been approved." if pending.is_new_app else '',Bundle_Name = pending.Bundle_Name, version = pending.Bundle_Version, submitter_name = pending.submitter.username, submitter_email = pending.submitter.email)
    send_mail('{Bundle_Name} App - Successfully Submitted.'.format(Bundle_Name = pending.Bundle_Name), msg, settings.EMAIL_ADDR, [pending.submitter.email], fail_silently=False)


def _send_email_for_accepted_app(to_email, from_email, Bundle_Name, Bundle_SymbolicName, server_url):
    subject = u'IGB App Store - {Bundle_Name} Has Been Approved'.format(Bundle_Name = Bundle_Name)
    app_url = reverse('app_page', args=[Bundle_SymbolicName])
    msg = u"""Your app has been approved! Here is your app page:

  {server_url}{app_url}

To edit your app page:
 1. Go to {server_url}{app_url}
 2. Sign in as {author_email}
 3. Under the "Editor's Actions" on the top-right, choose "Edit this page".

Make sure to add some tags to your app and a short app description, which is located
right below the app name. You can also add screenshots, details about your app,
and an icon to make your app distinguishable.

If you would like other people to be able to edit the app page, have them sign in
to the App Store, then add their email addresses to the Editors box, located in
the top-right.

- IGB App Store Team
""".format(app_url = app_url, author_email = to_email, server_url = server_url)
    send_mail(subject, msg, from_email, (to_email,))


def _get_server_url(request):
    name = request.META['SERVER_NAME']
    port = request.META['SERVER_PORT']
    if port == '80':
        return 'http://%s' % name
    elif port == '443':
        return 'https://%s' % name
    else:
        return 'http://%s:%s' % (name, port)


def _pending_app_accept(pending, request):
    # we always create a new app, because only new apps require accepting (old cytoscape behavior)
    """
        Update existing released app with Bundle_Name and different version and create new app if the
        app is not yet released
    """
    app, _ = App.objects.update_or_create(Bundle_Name=pending.Bundle_Name, Bundle_SymbolicName=pending.Bundle_SymbolicName)
    app.save()
    app.editors.add(pending.submitter)
    app.save()

    release = pending.make_release(app)
    release.active = True
    release.Bundle_Version = pending.Bundle_Version
    release.save()

    pending.delete_files()
    pending.delete()

    server_url = _get_server_url(request)
    _send_email_for_accepted_app(pending.submitter.email, settings.EMAIL_ADDR, app.Bundle_Name, app.Bundle_SymbolicName, server_url)


def _pending_app_decline(pending_app, request):
    pending_app.delete_files()
    pending_app.delete()


_PendingAppsActions = {
    'accept': _pending_app_accept,
    'decline': _pending_app_decline,
}


@login_required
def pending_apps(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    if request.method == 'POST':
        action = request.POST.get('action')
        if not action:
            return HttpResponseBadRequest('action must be specified')
        if not action in _PendingAppsActions:
            return HttpResponseBadRequest('invalid action--must be: %s' % ', '.join(_PendingAppsActions.keys()))
        pending_id = request.POST.get('pending_id')
        if not pending_id:
            return HttpResponseBadRequest('pending_id must be specified')
        try:
            pending_app = AppPending.objects.get(id = int(pending_id))
        except AppPending.DoesNotExist as ValueError:
            return HttpResponseBadRequest('invalid pending_id')
        _PendingAppsActions[action](pending_app, request)
        if request.is_ajax():
            return json_response(True)

    pending_apps = AppPending.objects.all().filter(submitter_approved=True)
    return html_response('pending_apps.html', {'pending_apps': pending_apps}, request)


# def _app_info(request_post):
#     Bundle_Name = request_post.get('app_fullname')
#     url = reverse('app_page', args=(Bundle_Name,))
#     exists = App.objects.filter(Bundle_Name = Bundle_Name, active = True).count() > 0
#     return json_response({'url': url, 'exists': exists})
#
#
# def _update_app_page(request_post):
#     Bundle_Name = request_post.get('Bundle_Name')
#     release_info = Release.objects.get(Bundle_Name=Bundle_Name)
#     if not Bundle_Name:
#         return HttpResponseBadRequest('"Bundle_Name" not specified')
#     app = get_object_or_none(App, Bundle_Name = Bundle_Name)
#     if app:
#         app.active = True
#     else:
#         app = App.objects.create(Bundle_Name = Bundle_Name)
#
#     Bundle_Description = request_post.get('Bundle_Description')
#     if Bundle_Description:
#         app.Bundle_Description = Bundle_Description
#
#     author_count = request_post.get('author_count')
#     if author_count:
#         author_count = int(author_count)
#         for i in range(author_count):
#             name = request_post.get('author_' + str(i))
#             if not name:
#                 return HttpResponseBadRequest('no such author at index ' + str(i))
#             institution = request_post.get('institution_' + str(i))
#             author, _ = Author.objects.get_or_create(name=name, institution=institution)
#             author_order = OrderedAuthor.objects.create(app=app, author=author, author_order = i)
#
#     app.save()
#     return json_response(True)


