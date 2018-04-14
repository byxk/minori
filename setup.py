from setuptools import setup

setup(
    name='Minori',
    version='0.1',
    packages=['Minori', 'Minori.actions'],
    install_requires=[
        'click',
        'feedparser',
    ],
    entry_points='''
        [console_scripts]
        minori=Minori.main:cli
    ''',
)
