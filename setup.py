# -{pip install -e .}
# -{del dist\* | python %f sdist bdist_wheel}
# -{twine upload dist/*}
"""
:copyright: (c) 2019 by K1DV5
:license: MIT, see LICENSE for more details.
"""

from setuptools import setup, find_packages
import pkg_resources

# sync with the core package
VERSION = pkg_resources.get_distribution('docal').version

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='docal-tkinter',
    author="Kidus Adugna",
    author_email='kidusadugna@gmail.com',
    classifiers=[
    #     'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="GUI implementation of docal with Tkinter",
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='docal',
    packages=['docal_tkinter'],
    url='https://github.com/K1DV5/docal-tkinter',
    version=VERSION,
    # zip_safe=False,
)

