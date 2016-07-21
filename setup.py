from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='autosar',
      version='0.1',
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
      packages=['autosar','autosar.parser'],
      zip_safe=False)
