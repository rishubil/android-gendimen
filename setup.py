from setuptools import setup

setup(name='android_gendimen',
      version='0.1',
      description='A simple tool for android dimens.xml',
      long_description='You can generate dimen tag for android by defining python expressions in xml comment.',
      keywords='android generator xml dimen dimension',
      url='http://github.com/rishubil/android_gendimen',
      author='Nesswit',
      author_email='rishubil@gmail.com',
      license='Apache License 2.0',
      packages=['android_gendimen'],
      install_requires=[
          'lxml',
          'python-graph-core'
      ],
      entry_points={
          'console_scripts': ['gendimen=android_gendimen:main'],
      },
      include_package_data=True,
      zip_safe=False)
