from setuptools import setup

setup(
    name='ASE-HW-Group7',
    version='0.1',
    description='Github repository for ASE HWs',
    author='Palash Rathod',
    author_email='prathod@ncsu.edu',
    packages=['src'],
        long_description="""\
            Creating github repository files.
            CODE_OF_CONDUCT.md
            CONTRIBUTING.md
            LICENSE.md
            CITATION.md
            INSTALL.md
            README.md
            setup.py
            src/
              Num.py
              Sym.py
              main.py
              misc.py
              test_engine.py
        """,
        classifiers=[
            "License :: MIT License",
            "Programming Language :: Python",
            "Development Status :: Planning",
            "Intended Audience :: Developers",
            "Topic :: Automated Software Engineering",
        ],
        keywords='requirements license python gitignore',
        license='MIT',
        )

