from setuptools import setup

setup(
    name='weather',
    version='0.1',
    author="Siddhant Dutta",
    description='A Python package in a form of a CLI for retrieving weather information with ease',
    license="MIT",
    author_email="forsomethingnewsid@gmail.com",
    url='https://github.com/elucidator8918/CoPilot_Hackathon_Weather_CLI',
    py_modules=['main'],
    python_requires='>=3.6',
    install_requires=['Click', 'Sphinx-Click', 'sphinx-autodoc-annotation',
                      'pytz', 'requests','getpass4'],
    entry_points={
        'console_scripts': [
            'weather = main:main'
            ]
        }
    )
