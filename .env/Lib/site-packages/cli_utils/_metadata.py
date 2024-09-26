# encoding: utf-8

# Variables for setup (these must be string only!)
__module_name__ = u'cli_utils'
__description__ = u''

__version__ = u'1.0.6'

__author__ = u'Hywel Thomas'
__authorshort__ = u'HT'
__authoremail__ = u'hywel.thomas@mac.com'

__license__ = u'MIT'

__githost__ = u'bitbucket.org'
__gituser__ = u'daycoder'
__gitrepo__ = u'cli_utils.git'


# Additional variables
__copyright__ = u'Copyright (C) 2018 {author}'.format(author=__author__)

__url__ = u'https://{host}/{user}/{repo}'.format(host=__githost__,
                                                 user=__gituser__,
                                                 repo=__gitrepo__)
__downloadurl__ = u'{url}/get/{version}.tar'.format(url=__url__,
                                                    version=__version__)
