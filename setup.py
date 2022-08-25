from setuptools import setup, find_packages


with open('README.txt') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='tramazroc',
    version='1.1.0',
    description='Paquete tratamiento macizos rocosos',
    long_description=readme,
    author='Kenneth Reitz',
    author_email='i52gusaj@uco.es',
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)