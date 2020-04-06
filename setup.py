from distutils.core import setup

setup(
    name='rekorder',
    description='Record and playback simple python CLI apps.',
    author='James Johnson',
    url='https://bitbucket.org/jcejohnson/rekorder/src/master/',
    version='0.4.0',
    packages=['rekorder'],
    license='Dont Be a Dick',
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': [
            # 'record=rekorder.cli.record:record',
            'rekorder=rekorder.cli.main:main',
        ],
    },
    install_requires=list(open('requires.txt').read().splitlines())
)
