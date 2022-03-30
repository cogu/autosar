from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='autosar',
      version='0.4.0',
      description='A set of Python modules for working with AUTOSAR XML files',
      long_description=readme(),
      long_description_content_type='text/x-rst',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing :: Markup :: XML',
      ],
      url='http://github.com/cogu/autosar',
      author='Conny Gustafsson',
      author_email='congus8@gmail.com',
      license='MIT',
	  install_requires=[
          'cfile>=0.1.4',
      ],
      packages=['autosar','autosar.parser','autosar.writer','autosar.rte', 'autosar.bsw', 'autosar.util'],
	  zip_safe=False,
	  test_suite='tests.my_test_suite')
