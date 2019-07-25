# Sample setup.py

from setuptools import setup

setup(
    name="quicy",
    keywords="python quic asyncio protocol",
    extras_require={'uvloop': ['uvloop']},
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=['quicy', ],
)