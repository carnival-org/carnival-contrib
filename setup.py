from setuptools import find_packages, setup  # type:ignore

requirements = [
    'carnival==2.0.0',
]

VERSION = "2.0.0"

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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=requirements,
    test_suite="tests",
)
