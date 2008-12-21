from setuptools import setup, find_packages
from os.path import join

name = 'atreal.speed'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()
readme = open("README.txt").read()
history = ""

setup(name = name,
      version = version,
      description = 'AtReal Speed',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'plone CMS zope',
      author = 'AtReal',
      # FIXME
      author_email = 'fixme@atreal.net',
      url = 'http://www.atreal.net',
      # FIXME
      download_url = 'http://pypi.python.org/pypi/atreal.speed',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['atreal'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires=[
        'setuptools',
        'plone.transforms'
      ],
      classifiers = [
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
