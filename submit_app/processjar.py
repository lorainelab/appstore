from zipfile import ZipFile, BadZipfile
from .mfparse import parse_manifest, max_of_lower_igb_pkg_versions, parse_app_dependencies
from apps.models import App, Release, VersionRE
from django.utils.encoding import smart_text
from util.view_util import get_object_or_none
import logging, io, sys

_MANIFEST_FILE_NAME = 'META-INF/MANIFEST.MF'
_REPOSITORY_FILE_NAME = 'repository.xml'
_MAX_MANIFEST_FILE_SIZE_B = 1024 * 1024
logger = logging.getLogger(__name__)


def process_jar(jar_file, expect_app_name):
    details_dict = {}
    try:
        archive = ZipFile(jar_file)
    except BadZipfile as IOError:
        raise ValueError('is not a valid zip file')

    manifest_file = _get_manifest_file(archive)
    manifest = parse_manifest(manifest_file)
    manifest_file.close()

    repository_file = _get_repository_file(archive)
    details_dict['repository'] = repository_file.read()
    repository_file.close()

    archive.close()

    is_osgi_bundle = True if manifest.get('Bundle-SymbolicName') else False
    parser_func = _parse_osgi_bundle if is_osgi_bundle else _parse_simple_app
    symbolicname = manifest.get('Bundle-SymbolicName')[0]
    if manifest.get('Bundle-Description') is not None:
        details_dict['details'] = manifest.get('Bundle-Description')[0]
    else:
        # If no description it says "No Description" in base64 below.
        details_dict['details'] = "Tm8gRGVzY3JpcHRpb24="
    app_name, app_ver, app_dependencies, has_export_pkg = parser_func(manifest)
    details_dict['has_export_pkg'] = has_export_pkg

    details_dict['fullname'] = smart_text(app_name, errors='replace')
    if expect_app_name and (not app_name == expect_app_name):
        raise ValueError('has app name as <tt>%s</tt> but must be <tt>%s</tt>' % (app_name, expect_app_name))
    details_dict['version'] = smart_text(app_ver, errors='replace')
    details_dict['symbolicname'] = smart_text(symbolicname, errors='replace')
    try:
        details_dict['app_dependencies'] = list(_app_dependencies_to_releases(app_dependencies))
    except ValueError as e:
        (msg, ) = e.args
        raise ValueError('has a problem with its manifest for entry <tt>IGB-App-Dependencies</tt>: ' + msg)
    return details_dict


def _app_dependencies_to_releases(app_dependencies):
    for dependency in app_dependencies:
        app_name, app_version = dependency

        app = get_object_or_none(App, active = True, fullname = app_name)
        if not app:
            raise ValueError('dependency on "%s": no such app exists' % app_name)

        release = get_object_or_none(Release, app = app, version = app_version, active = True)
        if not release:
            raise ValueError('dependency on "%s" with version "%s": no such release exists' % (app_name, app_version))

        yield release


def _get_manifest_file(zip_archive):
    try:
        manifest_info = zip_archive.getinfo(_MANIFEST_FILE_NAME)
    except KeyError:
        raise ValueError('does not have a manifest file located in <tt>%s</tt>' % _MANIFEST_FILE_NAME)

    if manifest_info.file_size > _MAX_MANIFEST_FILE_SIZE_B:
        raise ValueError('has a manifest file that\'s too large; it can be at most %d bytes but is %d bytes' % (_MAX_MANIFEST_FILE_SIZE_B, manifest_info.file_size))

    try:
        manifest_file = zip_archive.open(_MANIFEST_FILE_NAME , 'r')
        manifest_file = io.TextIOWrapper(manifest_file)
        return manifest_file
    except IOError:
        raise ValueError('does not have an accessible manifest file located in <tt>%s</tt>' % _MANIFEST_FILE_NAME)


def _get_repository_file(zip_archive):
    """
    Extract Repository File from the Bundle Package
    """
    try:
        repository_info = zip_archive.getinfo(_REPOSITORY_FILE_NAME)
    except KeyError:
        raise ValueError('does not have a repository file located inside the jar named <tt>%s</tt>' % _REPOSITORY_FILE_NAME)

    try:
        repository_file = zip_archive.open(_REPOSITORY_FILE_NAME, 'r')
        repository_file = io.TextIOWrapper(repository_file)
        return repository_file
    except IOError:
        raise ValueError('does not have an accessible repository file located inside the jar named <tt>%s</tt>' % _REPOSITORY_FILE_NAME)


def _last(d, k):
    v = d.get(k)
    return v[-1] if v else None


def _get_name_and_version(manifest, name_attr, version_attr):
    app_name = _last(manifest, name_attr)
    if not app_name:
        raise ValueError('does not have <tt>%s</tt> in its manifest' % name_attr)

    app_version = _last(manifest, version_attr)
    if not app_version:
        raise ValueError('does not have <tt>%s</tt> in its manifest' % version_attr)
    if not VersionRE.match(app_version):
        raise ValueError('<tt>%s</tt> does not follow this format: <i>major</i>[.<i>minor</i>][.<i>patch</i>][.<i>tag</i>]' % version_attr)

    return app_name, app_version


def _parse_simple_app(manifest):
    app_name, app_version = _get_name_and_version(manifest, 'IGB-App-Name', 'IGB-App-Version')

    # app_works_with = _last(manifest, 'IGB-API-Compatibility')
    # if not app_works_with:
    #     raise ValueError('does not have <tt>IGB-API-Compatibility</tt> in its manifest')

    app_dependencies = list() # simple apps can't have dependencies
    has_export_pkg = False # simple apps can't export packages

    return app_name, app_version, app_dependencies, has_export_pkg


def _ver_tuple_to_str(tup):
    return tup[0] + ('.' + tup[1] if tup[1] else '') + ('.' + tup[2] if tup[2] else '') + ('.' + tup[3] if tup[3] else '')


def _parse_osgi_bundle(manifest):
    app_name, app_version = _get_name_and_version(manifest, 'Bundle-Name', 'Bundle-Version')

    # Use the Below line to find the Max Version for the App (App Compatible with which version of IGB)
    # import_packages = manifest.get('Import-Package')
    # if not import_packages:
    #     raise ValueError('does not import any packages--<tt>Import-Package</tt> is not in its manifest')
    #import_packages = ','.join(import_packages)
    #max_ver = max_of_lower_igb_pkg_versions(import_packages)

    app_dependencies_str = _last(manifest, 'IGB-App-Dependencies')
    if app_dependencies_str:
        try:
            app_dependencies = list(parse_app_dependencies(app_dependencies_str))
        except ValueError as e:
            (msg, ) = e.args
            raise ValueError('has a problem with the <tt>IGB-App-Dependencies</tt> entry: ' + msg)
    else:
        app_dependencies = list()

    has_export_pkg_str = _last(manifest, 'Export-Package')
    has_export_pkg = True if has_export_pkg_str else False

    return app_name, app_version, app_dependencies, has_export_pkg
