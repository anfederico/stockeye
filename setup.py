from distutils.core import setup

setup(name='stockeye',
      version='v0.6',
      description='Keep track of short term stock movement by monitoring breaking news activity',
      author='Anthony Federico',
      author_email='dephoona@gmail.com',
      url='https://github.com/anfederico/Stockeye',
      packages=['stockeye'],
      scripts=['bin/stockeye-corpus']
     )