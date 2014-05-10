from setuptools import setup, find_packages
import os

version = '2.3.dev0'

setup(name='Products.ARFilePreview',
      version=version,
      description="Enables preview mode for common file formats such as pdf, word etc.",
      long_description=open("README.txt").read() + "\n\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='atReal',
      author_email='contact@atreal.net',
      url='http://plone.org/products/arfilepreview',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
