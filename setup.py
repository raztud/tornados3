from setuptools import setup

setup(name='tornados3',
      version='0.1',
      description='Tornado async manager for AWS S3',
      #url='http://github.com/storborg/funniest',
      author='Razvan Tudorica',
      #author_email='',
      license='MIT',
      packages=['tornados3'],
      install_requires=[
          'botocore',
      ],
      zip_safe=False)

