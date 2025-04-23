from setuptools import setup

version = __import__('py_pkpass').__version__

setup(
    name='py-pkpass',
    version=version,
    author='GlitchOo',
    packages=['py_pkpass', 'py_pkpass.test'],
    url='https://github.com/GlitchOo/py-pkpass/',
    license=open('LICENSE.txt').read(),
    description='Pkpass file generator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    download_url='https://github.com/GlitchOo/py-pkpass/archive/refs/tags/v%s.tar.gz' % version,

    install_requires=[
        'cryptography>=44.0.1',
    ],
    extras_require={
        ':python_version>="3.10"': ['swig'],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
