from setuptools import setup

setup(
    name='tornados3',
    version='0.1',
    description='Tornado async manager for AWS S3',
    url='https://github.com/raztud/tornados3',
    author='Razvan Tudorica',
    license='MIT',
    packages=['tornados3'],
    install_requires=[
        'botocore',
        'tornado'
    ],
    zip_safe=False
)
