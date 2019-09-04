from zipfile import ZipFile, BadZipfile
import requests, io
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
    if isinstance(jar_file,str):
        file_obj = requests.get(jar_file)
    else:
        file_obj = None

    try:
        if file_obj is not None:
            archive = ZipFile(io.BytesIO(file_obj.content))
        else:
            archive = ZipFile(jar_file)
    except BadZipfile as IOError:
        raise ValueError('%s cannot be read as a zip file.'%jar_file)

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
    return details_dict


def _get_manifest_file(zip_archive):
    try:
        manifest_info = zip_archive.getinfo(_MANIFEST_FILE_NAME)
    except KeyError:
        raise ValueError('%s lacks a MANIFEST.MF file' % _MANIFEST_FILE_NAME)

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
    Extract OBR index file (repository.xml) from the IGB App OSGi bundle
    """
    try:
        repository_info = zip_archive.getinfo(_REPOSITORY_FILE_NAME)
    except KeyError:
        raise ValueError('<tt>%s</tt> lacks repository.xml OBR index file.' % _REPOSITORY_FILE_NAME)

    try:
        repository_file = zip_archive.open(_REPOSITORY_FILE_NAME, 'r')
        repository_file = io.TextIOWrapper(repository_file)
        return repository_file
    except IOError:
        raise ValueError('<tt>%s</tt> contains inacessible repository.xml OBR index file.' % _REPOSITORY_FILE_NAME)


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

def _ver_tuple_to_str(tup):
    return tup[0] + ('.' + tup[1] if tup[1] else '') + ('.' + tup[2] if tup[2] else '') + ('.' + tup[3] if tup[3] else '')


def _parse_osgi_bundle(manifest):
    app_name, app_version = _get_name_and_version(manifest, 'Bundle-Name', 'Bundle-Version')
    app_dependencies = list() # remove this later; return 2 items instead of 3
    has_export_pkg_str = _last(manifest, 'Export-Package')
    has_export_pkg = True if has_export_pkg_str else False

    return app_name, app_version, app_dependencies, has_export_pkg
