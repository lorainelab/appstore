import collections
import datetime
# Returns a unicode string encoded in a cookie
import logging
import re
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import F
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
import html

from apps.models import App, Author, OrderedAuthor, Screenshot, Release
from submit_app.models import AppPending
from curated_categories.models import CuratedCategory, CuratedCategoriesMapping
from download.models import ReleaseDownloadsByDate
from util.id_util import fullname_to_name
from util.img_util import scale_img
from util.view_util import json_response, html_response, obj_to_dict, get_object_or_none
from haystack.query import SearchQuerySet
from django.shortcuts import redirect
logger = logging.getLogger(__name__)


def _unescape_and_unquote(s):
	if not s: return s
	return html.unescape(unquote(s))


# ============================================
#      Nav Panel
# ============================================

_NavPanelContextCache = None


def _nav_panel_context(request):
	global _NavPanelContextCache

	if _NavPanelContextCache:
		return _NavPanelContextCache

	all_curated_categories = {}
	curated_cat_description = {}

	curated_categories = CuratedCategory.objects.all()
	for categories in curated_categories:
		if categories.curated_category_type in all_curated_categories:
			all_curated_categories[categories.curated_category_type].append(categories)
		else:
			all_curated_categories[categories.curated_category_type] = [categories]
		curated_cat_description[categories.curated_category_type] = categories.type_description
		curated_cat_description[categories.curated_category] = categories.curated_category_description

	result = {
		'all_curated_categories': all_curated_categories,
		'curated_cat_description': curated_cat_description
	}

	_NavPanelContextCache = result

	return result


def _flush_tag_caches():
	global _NavPanelContextCache
	global _TagCountCache
	_NavPanelContextCache = None
	_TagCountCache = dict()


# ============================================
#      Navigating Apps & Tags
# ============================================

class _DefaultConfig:
	num_of_top_apps = 6


def apps_default(request):

	apps = App.objects.order_by('Bundle_Name')
	releases = {}
	downloaded_apps = dict()
	for app in apps:
		released_app = Release.objects.filter(active=True, app=app).order_by('-created').first()
		if released_app:
			releases[app] = released_app
		releases_obj = Release.objects.filter(app=app)
		total_download = 0
		for release in releases_obj:
			downloads = ReleaseDownloadsByDate.objects.filter(release=release)
			for download in downloads:
				total_download += download.count
		downloaded_apps[app] = total_download
	sorted_dict = collections.OrderedDict(sorted(downloaded_apps.items(), key=lambda kv: kv[1], reverse=True))
	c = {
		'releases': releases,
		'downloaded_apps_pg': sorted_dict.keys(),
		'navbar_selected_link': 'all',
		'search_query': '',
		'selected_tag_name': '',
	}
	return html_response('apps/apps_default.html', c, request, processors=(_nav_panel_context,))

def apps_with_tag(request, tag_name):
	apps = []
	releases = dict()
	curated_cat = None

	try:
		curated_cat = CuratedCategory.objects.get(curated_category=tag_name)
		apps = CuratedCategoriesMapping.objects.filter(curated_categories=curated_cat)
		for app_query in apps:
			released_app = Release.objects.filter(active=True, app=app_query.app).order_by('-created').first()
			if released_app:
				releases[app_query.app] = released_app
	except CuratedCategoriesMapping.DoesNotExist:
		pass

	c = {
		'curated_cat': curated_cat,
		'apps': apps,
		'releases': releases,
		'selected_tag_name': tag_name
	}
	return html_response('apps/apps_with_tag.html', c, request, processors=(_nav_panel_context,))


def apps_with_author(request, author_name):
	releases_obj = Release.objects.filter(active=True, authors__name__exact=author_name).order_by('-created')
	releases = {}
	apps = []

	for release in releases_obj:
		releases[release.app] = release
		apps.append(release.app)
	if not releases:
		raise Http404('No such author "%s".' % author_name)

	apps = list(set(apps))

	c = {
		'author_name': author_name,
		'apps': apps,
		'releases': releases
	}
	return html_response('apps/apps_with_author.html', c, request, processors=(_nav_panel_context,))



# ============================================
#      App Pages
# ============================================

# -- App Rating


def _app_rate(app, user, post, latest_release):
	rating_n = post.get('rating')
	releases=Release.objects.filter(active=True, app=app).order_by('-created')
	try:
		rating_n = int(rating_n)
		if not (0 <= rating_n <= 5):
			raise ValueError()
	except ValueError:
		raise ValueError('rating is "%s" but must be an integer between 0 and 5' % rating_n)
	latest_release.stars = rating_n
	stars = 0
	for i in range(1, releases.count()):
		stars += releases[i].stars
	app.stars = stars + rating_n
	app.save()
	latest_release.save()
	return obj_to_dict(app, (['stars_percentage']))


def _app_ratings_delete_all(app, user, post):
	if not app.is_editor(user):
		return HttpResponseForbidden()
	app.stars = 0
	app.save()
	releases = Release.objects.filter(active=True, app=app).order_by('-created')
	for release in releases:
		release.stars =0
		release.save()


def _installed_count(app, user, post, release):
	"""
	:param app: Current App
	:param user: Current User (Not Required by the Function but required by the model)
	:param post: Dictionary containing Action and Status Keys
	:return: True (Dummy Response | Can be change if another use case)
	"""
	state = post.get('status')
	if state == "Installed":
		ReleaseDownloadsByDate.objects.get_or_create(release=release, when=datetime.date.today())
		ReleaseDownloadsByDate.objects.filter(release=release, when=datetime.date.today()).update(count = F('count')+1)
	return json_response('True')

# -- General app stuff


def _mk_app_page(app, released_apps, user, request, decoded_details, download_count, curated_category_mapping):
	c = {
		'app': app,
		'released_apps': released_apps,
		'decoded_details': decoded_details,
		'download_count': download_count,
		'latest_released': released_apps[0],
		'is_logged_in': (user != None),
		'is_editor': app.is_editor(user),
		'search_query': '',
		'repository_url': get_host_url(request) + '/obr/releases',
		'curated_category_mapping': curated_category_mapping
	}
	return html_response('apps/app_page.html', c, request)


_AppActions = {
	'rate': _app_rate,
	'ratings_delete_all': _app_ratings_delete_all,
}


def get_host_url(request):
	host_name = request.get_host()
	port = request.META['SERVER_PORT']
	if port == '443':
		return 'https://%s' % host_name
	else:
		return 'http://%s' % host_name


def string_to_array(version, delem):
	version = version.split(delem)
	version = ''.join(x for x in version)
	return int(version)


def install_app(request, path):
    result = path.split('/')
    if result[0] != 'pending_releases':
        app = App.objects.get(Bundle_SymbolicName=result[0])
        release = Release.objects.get(app=app, Bundle_Version=result[2])
        ReleaseDownloadsByDate.objects.get_or_create(release=release, when=datetime.date.today())
        ReleaseDownloadsByDate.objects.filter(release=release, when=datetime.date.today()).update(count=F('count') + 1)
    if settings.USE_S3:
        return HttpResponseRedirect('https://' + settings.AWS_S3_CUSTOM_DOMAIN + '/' + settings.AWS_LOCATION + '/' + path)
    else:
        return HttpResponseRedirect('/media/' + path)


def app_page(request, app_name):
	app = get_object_or_404(App, Bundle_SymbolicName=app_name)
	curated_category_mapping = get_object_or_none(CuratedCategoriesMapping, app=app)
	released_apps = Release.objects.filter(active=True, app=app).order_by('-created')
	latest_release = Release.objects.filter(active=True, app=app).order_by('-created').first()
	decoded_details = latest_release.Bundle_Description
	download_count = 0
	for release in released_apps:
		downloads = ReleaseDownloadsByDate.objects.filter(release=release)
		if downloads.count() > 0:
			for download in downloads:
				download_count += download.count
	# temporarily remove if condition if you want any user to rate
	user = request.user if request.user.is_authenticated else None
	if request.user.is_authenticated:
		if request.method == 'POST':
			action = request.POST.get('action')
			if not action:
				return HttpResponseBadRequest('no action specified')
			if not action in _AppActions:
				return HttpResponseBadRequest('action "%s" invalid--must be: %s' % (action, ', '.join(_AppActions)))
			try:
				result = _AppActions[action](app, user, request.POST, latest_release)
			except ValueError as e:
				return HttpResponseBadRequest(str(e))
			if isinstance(result, HttpResponse):
				return result
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				return json_response(result)
	return _mk_app_page(app, released_apps, user, request, decoded_details, download_count, curated_category_mapping)

# ============================================
#      App Page Editing
# ============================================


@login_required
def author_names(app, request):
	names = [a.name for a in Author.objects.exclude(name__isnull=True)]
	return json_response(names)


@login_required
def institution_names(app, request):
	names = [a.institution for a in Author.objects.exclude(institution__isnull=True)]
	return json_response(names)


isoDateRe = re.compile(r'(\d{4})-(\d{2})-(\d{2})')


def _parse_iso_date(string):
	matches = isoDateRe.match(string)
	if not matches:
		raise ValueError('date does not follow format: yyyy-mm-dd')
	year, month, day = matches.groups()
	try:
		return datetime.date(int(year), int(month), int(day))
	except ValueError:
		return None


def _mk_basic_field_saver(field, func=None):
	"""
	Basic Field Saver for Different Fields in App Edit Page
	Helper Function to Help Edit the Page
	"""
	def saver(app, request, release):
		value = request.POST.get(field)
		if value == None:
			raise ValueError('no %s specified' % field)
		if value == '':
			value = None
		elif func:
			value = func(value)
		setattr(release, field, value)

	return saver

def _save_curated_categories(app, request, release):
	tag_count = request.POST.get('count')
	if not tag_count:
		raise ValueError('no tag_count specified')
	try:
		tag_count = int(tag_count)
	except ValueError:
		raise ValueError('tag_count is not an integer')

	tags = []
	for i in range(tag_count):
		tag_key = 'cat_' + str(i)
		tag = request.POST.get(tag_key)
		if not tag:
			raise ValueError('expected ' + tag_key)
		tags.append(tag)
	app_mapping, _ = CuratedCategoriesMapping.objects.get_or_create(app=app)
	app_mapping.curated_categories.clear()
	for tag in tags:
		tag_obj = CuratedCategory.objects.get(curated_category=tag)
		app_mapping.curated_categories.add(tag_obj)

	_flush_tag_caches()


class _AppPageEditConfig:
	max_img_size_b = 2 * 1024 * 1024
	max_icon_dim_px = 64
	thumbnail_height_px = 150
	app_description_maxlength = 140


def _upload_logo(app, request, release):
	f = request.FILES.get('file')
	if not f:
		raise ValueError('no file submitted')
	if f.size > _AppPageEditConfig.max_img_size_b:
		raise ValueError(
			'image file is %d bytes but can be at most %d bytes' % (f.size, _AppPageEditConfig.max_img_size_b))
	release.delete_logo()
	release.logo.save(f.name, f)
	release.save()


def _upload_screenshot(app, request, release):
	screenshot_f = request.FILES.get('file')
	if not screenshot_f:
		raise ValueError('no file submitted')
	if screenshot_f.size > _AppPageEditConfig.max_img_size_b:
		raise ValueError('image file is %d bytes but can be at most %d bytes' % (
		screenshot_f.size, _AppPageEditConfig.max_img_size_b))
	thumbnail_f = scale_img(screenshot_f, screenshot_f.name, _AppPageEditConfig.thumbnail_height_px, 'h')
	screenshot = Screenshot.objects.create(release=release)
	screenshot.screenshot.save(screenshot_f.name, screenshot_f)
	screenshot.thumbnail.save(thumbnail_f.name, thumbnail_f)
	screenshot.save()


def _delete_screenshot(app, request, release):
	screenshot_id = request.POST.get('screenshot_id')
	if not screenshot_id:
		raise ValueError('no screenshot_id specified')

	try:
		screenshot_id = int(screenshot_id)
		screenshot = Screenshot.objects.get(id=screenshot_id)
	except (ValueError, Screenshot.DoesNotExist) as e:
		raise ValueError('invalid screenshot_id')
	screenshot.delete()


def _check_editor(app, request, release):
	editor_email = request.POST.get('editor_email')
	if not editor_email:
		raise ValueError('no editor_email specified')
	user = get_object_or_none(User, email=editor_email)
	return user.username if user else False


def _save_editors(app, request, release):
	editors_count = request.POST.get('editors_count')
	if not editors_count:
		raise ValueError('no editors_count specified')
	try:
		editors_count = int(editors_count)
	except ValueError:
		raise ValueError('editors_count is not an integer')

	usernames = list()
	for i in range(editors_count):
		key = 'editor_' + str(i)
		username = request.POST.get(key)
		if not username:
			raise ValueError('expected ' + key)
		usernames.append(username)

	app.editors.clear()
	for username in usernames:
		user = get_object_or_none(User, username=username)
		if not user:
			raise ValueError('invalid username: ' + username)
		app.editors.add(user)


def _save_authors(app, request, release):
	authors_count = request.POST.get('authors_count')
	if not authors_count:
		raise ValueError('no authors_count specified')
	try:
		authors_count = int(authors_count)
	except ValueError:
		raise ValueError('authors_count is not an integer')

	authors = list()
	for i in range(authors_count):
		key = 'author_' + str(i)
		name = request.POST.get(key)
		if not name:
			raise ValueError('expected ' + key)
		institution = request.POST.get('institution_' + str(i))
		if not institution:
			institution = None
		authors.append((name, institution, i))

	release.authors.clear()
	for name, institution, author_order in authors:
		author, _ = Author.objects.get_or_create(name=name, institution=institution)
		ordered_author = OrderedAuthor.objects.create(release=release, author=author, author_order=author_order)


def _save_release_notes(app, request, release):
	release_count = request.POST.get('release_count')
	if not release_count:
		raise ValueError('no release_count specified')
	try:
		release_count = int(release_count)
	except ValueError:
		raise ValueError('release_count is not an integer')

	for i in range(release_count):
		key = 'release_id_' + str(i)
		release_id = request.POST.get(key)
		if not release_id:
			raise ValueError('expected ' + key)
		try:
			release = Release.objects.get(id=int(release_id))
		except (Release.DoesNotExist, ValueError) as e:
			raise ValueError('release_id "%s" is invalid' % release_id)
		notes_key = 'notes_' + str(i)
		notes = request.POST.get(notes_key)
		if notes is None:
			raise ValueError('expected ' + notes_key)
		release.notes = notes
		release.save()


def _delete_release(app, request, back_release):
	release_count = request.POST.get('release_count')
	if not release_count:
		raise ValueError('no release_count specified')
	try:
		release_count = int(release_count)
	except ValueError:
		raise ValueError('release_count is not an integer')

	for i in range(release_count):
		key = 'release_id_' + str(i)
		release_id = request.POST.get(key)
		if not release_id:
			raise ValueError('expected ' + key)
		try:
			release = Release.objects.get(id=int(release_id))
		except (Release.DoesNotExist, ValueError) as e:
			raise ValueError('release_id "%s" is invalid' % release_id)
		release.active = False
		release.save()
		app_id = release.app_id

_AppEditActions = {
	'save_short_title': _mk_basic_field_saver('short_title'),
	'save_license_url': _mk_basic_field_saver('license_url'),
	'save_license_confirm': _mk_basic_field_saver('license_confirm', func=lambda s: s.lower() == 'true'),
	'save_website_url': _mk_basic_field_saver('website_url'),
	'save_platform_compatibility': _mk_basic_field_saver('platform_compatibility'),
	'save_tutorial_url': _mk_basic_field_saver('tutorial_url'),
	'save_citation': _mk_basic_field_saver('citation'),
	'save_code_repository_url': _mk_basic_field_saver('code_repository_url'),
	'save_contact_email': _mk_basic_field_saver('contact_email'),
	'save_bundle_description': _mk_basic_field_saver('Bundle_Description'),
	'save_curated_categories': _save_curated_categories,
	'upload_logo': _upload_logo,
	'upload_screenshot': _upload_screenshot,
	'delete_screenshot': _delete_screenshot,
	'check_editor': _check_editor,
	'save_editors': _save_editors,
	'save_authors': _save_authors,
	'save_release_notes': _save_release_notes,
	'delete_release': _delete_release,
}

"""
Flow: app_page_edit -> result[following code] -> _AppEditActions -> Find Action ->
			Go to the Function -> Do Processing -> Return -> Save App -> Save Releases
"""


@login_required
def app_page_edit(request, app_name):
	"""
	On Click : Save
	Function Call: app_page_edit
	Request: HTTP Request
	Request Content: action from one of the actions above.
	app_name: Bundle Symbolic Name
	"""
	app = get_object_or_404(App, Bundle_SymbolicName=app_name)
	released_apps = Release.objects.filter(active=True, app=app).order_by('-created')
	latest_released = released_apps.first()
	if not app.is_editor(request.user):
		return HttpResponseForbidden()
	if request.method == 'POST':
		action = request.POST.get('action')
		if not action:
			return HttpResponseBadRequest('no action specified')
		if not action in _AppEditActions:
			return HttpResponseBadRequest('action "%s" invalid--must be: %s' % (action, ', '.join(_AppEditActions)))
		try:
			"""
			Result gets the App and Release Value
			"""
			result = _AppEditActions[action](app, request, latest_released)
		except ValueError as e:
			return HttpResponseBadRequest(str(e))
		except App.DoesNotExist:
			return HttpResponseRedirect('all/')
		app.save()
		latest_released.save()
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return json_response(result)


	# -- IGBF-2520 -- START --
	curated_cat = {}
	for category_obj in CuratedCategory.objects.all():
		if category_obj.curated_category_type in curated_cat.keys():
			curated_cat[category_obj.curated_category_type].append(category_obj.curated_category)
		else:
			curated_cat[category_obj.curated_category_type] = [category_obj.curated_category]
	# -- IGBF-2520 -- END --
	mapped_cc = []
	for mapping in CuratedCategoriesMapping.objects.filter(app=app):
		for cc in mapping.curated_categories.all():
			mapped_cc.append(cc)

	# print(mapped_cc)
	c = {
		'app': app,
		'latest_released': latest_released,
		'released_apps': released_apps,
		'mapped_cc': mapped_cc,
		'curated_cat': curated_cat,
		'max_file_img_size_b': _AppPageEditConfig.max_img_size_b,
		'max_icon_dim_px': _AppPageEditConfig.max_icon_dim_px,
		'thumbnail_height_px': _AppPageEditConfig.thumbnail_height_px,
		'app_description_maxlength': _AppPageEditConfig.app_description_maxlength,
	}
	return html_response('apps/app_page_edit.html', c, request)


def custom_search_query(request):
	"""
	This function strips the double quotes around the string that is to be searched
	and searches whatever fields are marked ``document=True``
	:param request:
	:return:
	"""
	query_string = request.GET.get('q', None).strip("\"")
	if len(query_string)==0:
		return redirect('/')
	sqs = SearchQuerySet().auto_query(query_string).load_all()
	setsqs = set()
	for release in sqs:
		setsqs.add(release.object.app)
	if len(setsqs) <= 0:
		return html_response('search/search.html', {'object_list': setsqs, 'query_string': query_string}, request, processors=(_nav_panel_context,))
	else:
		return html_response('search/search.html', {'object_list': setsqs}, request, processors=(_nav_panel_context,))
