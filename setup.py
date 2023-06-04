from setuptools import setup

setup(
    name='weather',
    version='1.1',
    author="Siddhant Dutta",
    author_email="forsomethingnewsid@gmail.com",
    py_modules=['main'],
    install_requires=['Click', 'Sphinx-Click', 'sphinx-autodoc-annotation',
                      'pytz', 'requests','getpass4'],
    entry_points={
        'console_scripts': [
            'weather = main:main'
            ]
        }
    )
