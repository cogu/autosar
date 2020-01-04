from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='autosar',
      version='0.3.8',
      description='autosar python module',
      long_description=readme(),
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
	  dependency_links=['https://github.com/cogu/cfile/archive/v0.1.4.tar.gz#egg=cfile-0.1.4'],
	  zip_safe=False,
	  test_suite='tests.my_test_suite')
