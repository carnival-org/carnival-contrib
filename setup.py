from setuptools import setup, find_packages  # type:ignore


requirements = [
    'carnival>=0.7,<1.0',
]

VERSION = "0.5"

setup(
    name='carnival_contrib',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/carnival-org/carnival-contrib',
    license='MIT',
    author='a1fred',
    author_email='demalf@gmail.com',
    description='Carnival community receipts',
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
    ],
    install_requires=requirements,
    test_suite="tests",
)
