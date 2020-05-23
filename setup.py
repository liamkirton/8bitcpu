from distutils.core import setup


setup(name='8bitcpu',
      version='1.0',
      description='8bitcpu',
      author='Liam Kirton',
      author_email='liam@int3.ws',
      packages=['bootstrap'],
      install_requires=[
          'at28c256',
      ])
