from setuptools import setup

setup(
    name='my_utils',
    version='0.1.1',
    author='Faisal Alsajjan',
    author_email='fta.sajjan@gmail.com',
    packages=['my_utils', 'my_utils.test'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Collection of utility modules',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
