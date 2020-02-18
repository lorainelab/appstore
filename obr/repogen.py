#
# Author: Sameer Shanbhag
# Email: sshanbh1@uncc.edu
#

import base64
from xml.etree import ElementTree as ET
from apps.models import Release
from submit_app.models import AppPending


def get_bundle_symbolic_name(input):
    """
    :param input: Complete Name of the application
    :return: lower cased name
    """
    input = input.lower()
    input = input.replace(' ', '')
    return input


def xml_generator(dict_ver, gen_tree, tree, state):
    """
    :param gen_tree: Final Element Tree After each Iteration
    :param dict_ver: App Object Data
    :param tree: Element Tree Retrieved from Jar
    :param state: Pending or Released ?
    :return: Nothing | Generates the XML at a given location
    """
    gen_tree = ET.tostring(gen_tree, encoding='unicode')
    gen_tree = ET.fromstring(gen_tree)
    super_tree = gen_tree

    tree = ET.tostring(tree, encoding='unicode')
    tree = ET.fromstring(tree)
    cur_tree = tree

    current_resource = cur_tree.find('resource')
    curr_desc = current_resource.find('description')

    if curr_desc is not None:
        curr_desc.text = base64.b64encode(bytes(dict_ver.Bundle_Description, 'utf-8')).decode('utf-8')
    else:
        curr_desc = ET.SubElement(current_resource, 'description')
        curr_desc.text = base64.b64encode(bytes(dict_ver.Bundle_Description, 'utf-8')).decode('utf-8')

    if state == 'pending':
        current_resource.set('uri', '/installapp/pending_releases/' + dict_ver.release_file.name)
    else:
        current_resource.set('uri', '/installapp/' + str(dict_ver.release_file.name))

    super_tree.append(current_resource)
    return super_tree


def initial_generation(dict_ver, state):
    """
    :param dict_ver: App Info Object
    :param tree: Element Object
    :param state: Pending or Released ?
    :return: ElementTree
    """
    element_tree = ET.fromstring(dict_ver.repository_xml)
    current_resource = element_tree.find('resource')
    curr_desc = current_resource.find('description')

    if state == 'pending':
        current_resource.set('uri', '/installapp/pending_releases/' + dict_ver.release_file.name)
    else:
        current_resource.set('uri', '/installapp/' + str(dict_ver.release_file.name))

    if curr_desc is not None:
        curr_desc.text = base64.b64encode(bytes(dict_ver.Bundle_Description, 'utf-8')).decode('utf-8')
    else:
        curr_desc = ET.SubElement(current_resource, 'description')
        curr_desc.text = base64.b64encode(bytes(dict_ver.Bundle_Description, 'utf-8')).decode('utf-8')
        
    return element_tree


def main(status):
    if status == 'pending':
        all_entries = AppPending.objects.all()
    else:
        all_entries = Release.objects.filter(active=True)
    gen_tree = ""
    if len(all_entries) > 0:
        for i in range(0, len(all_entries)):
            if i == 0:
                gen_tree = initial_generation(all_entries[i], status)
            else:
                tree = ET.fromstring(all_entries[i].repository_xml)
                gen_tree = xml_generator(all_entries[i], gen_tree, tree, status)
        return gen_tree
    else:
        repository = ET.Element('repository')
        resource = ET.SubElement(repository, 'resource')
        return repository
