from setuptools import setup

setup(
    name='minori',
    version='0.1',
    py_modules=['minori'],
    install_requires=[
        'click',
        'feedparser',
    ],
    entry_points='''
        [console_scripts]
        minori=main:cli
    ''',
)
