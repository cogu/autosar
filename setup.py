from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='autosar',
      version='0.4.2',
      description='A set of Python modules for working with AUTOSAR XML files',
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing :: Markup :: XML',
      ],
      url='http://github.com/cogu/autosar',
      project_urls={
        'Documentation': 'https://autosar.readthedocs.io/'
      },
      author='Conny Gustafsson',
      author_email='congus8@gmail.com',
      license='MIT',
	  install_requires=[
          'cfile==0.2.0',
      ],
      packages=['autosar','autosar.parser','autosar.writer','autosar.rte', 'autosar.bsw', 'autosar.util'],
	  zip_safe=False,
	  test_suite='tests.my_test_suite')
