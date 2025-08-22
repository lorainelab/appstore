import re

_non_alphanum_re = re.compile(r'[\W_]+')


def fullname_to_name(fullname):
    return _non_alphanum_re.sub('', fullname).lower()
