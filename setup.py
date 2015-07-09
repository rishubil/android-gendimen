from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='android-gendimen',
      version='0.1',
      description='A simple tool for android dimens.xml',
      long_description='You can generate dimen tag for android by defining python expressions in xml comment.',
      keywords='android generator xml dimen dimension',
      url='http://github.com/rishubil/android-gendimen',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Code Generators'
      ],
      author='Nesswit',
      author_email='rishubil@gmail.com',
      license='Apache License 2.0',
      packages=['gendimen'],
      install_requires=[
          'lxml',
          'python-graph-core'
      ],
      entry_points={
          'console_scripts': ['gendimen=gendimen:main'],
      },
      include_package_data=True,
      zip_safe=False)
