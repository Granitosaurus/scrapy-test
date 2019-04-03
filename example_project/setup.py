from setuptools import setup


setup(
    name='example-crawler',
    version='1.0',
    packages=['example', 'tests'],
    url='https://gitlab.com/granitosaurus/scrapy-test',
    license='GPLv3',
    author='granitosaurus',
    author_email='granitosaurus@pm.me',
    description='scrapy output testing framework',
    install_requires=[
        # todo scrapytests
        'scrapy',
    ]
)
