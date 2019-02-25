from setuptools import setup

setup(
    name='scrapytest',
    version='0.1',
    packages=['scrapytest'],
    url='https://gitlab.com/granitosaurus/scrapy-test',
    license='GPLv3',
    author='granitosaurus',
    author_email='granitosaurus@pm.me',
    description='scrapy output testing framework',
    entry_points={
        'console_scripts': [
            f'scrapy-test=scrapytest.cli:main'
        ],
    },
)
