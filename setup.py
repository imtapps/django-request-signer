import os
from distutils.core import Command
from setuptools import find_packages, setup

REQUIREMENTS = ['Django', 'south']

def do_setup():
    setup(
        name='django-request-signer',
        version='0.0.2',
        author='imtapps',
        url='https://github.com/imtapps/django-request-signer',
        description="A python library for signing http requests.",
        long_description=open('README.rst', 'r').read(),
        install_requires=REQUIREMENTS,
        packages=find_packages(exclude=['example']),
        cmdclass={
            'install_dev': InstallDependencies,
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'License :: OSI Approved :: BSD License',
            'Topic :: Internet',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

class InstallDependencies(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("pip install %s" % ' '.join(REQUIREMENTS))
        os.system("pip install -r test_requirements.txt")

if __name__ == '__main__':
    do_setup()
