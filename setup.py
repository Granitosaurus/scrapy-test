from setuptools import setup

with open('readme.md') as f:
    long_description = f.read()

setup(
    name='scrapy-test',
    version='0.1',
    packages=['scrapytest'],
    url='https://gitlab.com/granitosaurus/scrapy-test',
    license='GPLv3',
    author='granitosaurus',
    author_email='granitosaurus@pm.me',
    description='scrapy output testing framework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'click',
        'scrapy',
    ],
    entry_points={
        'console_scripts': [
            f'scrapy-test=scrapytest.cli:main'
        ],
    },
)
