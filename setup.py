import os
from distutils.core import Command
from setuptools import find_packages, setup

REQUIREMENTS = ['Django', 'south']

def do_setup():
    setup(
        name='django-request-signer',
        version='0.0.2',
        install_requires=REQUIREMENTS,
        packages=find_packages(exclude=['example']),
        cmdclass={
            'install_dev': InstallDependencies,
        }
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
