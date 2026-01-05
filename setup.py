#!/usr/bin/env python

from setuptools import setup
from glob import glob

__license__ = "GPL"
__version__ = "2.6.4"
__maintainer__ = "Langille Lab"

long_description = ("Douglas et al. 2020. PICRUSt2 for prediction of "
                    "metagenome functions. Nature Biotechnology. doi: "
                    "10.1038/s41587-020-0548-6.")

setup(name='PICRUSt2',
      version=__version__,
      description=('PICRUSt: Phylogenetic Investigation of Communities by '
                   'Reconstruction of Unobserved States'),
      maintainer=__maintainer__,
      url='https://github.com/picrust/picrust2/wiki',
      packages=['picrust2'],
      package_dir={'picrust2': 'picrust2'},
      scripts=glob('scripts/*py'),
      install_requires=[
          'numpy',
          'h5py',
          'joblib',
          'biom-format'
      ],
      package_data={'picrust2':
                    ['MinPath/MinPath12hmp.py',
                     'Rscripts/*R',
                     'default_files/prokaryotic/*',
                     'default_files/prokaryotic/pro_ref/*',
                     'default_files/pathway_mapfiles/*',
                     'default_files/description_mapfiles/*',
                     'default_files/archaea/*',
                     'default_files/archaea/arc_ref/*',
                     'default_files/bacteria/*',
                     'default_files/bacteria/bac_ref/*',
                     'default_files/fungi/*',
                     'default_files/fungi/fungi_ITS/*'
                     ]},
      long_description=long_description)
