from setuptools import setup, find_packages

setup(
    name='SalletNodePackage',              # Name of the package
    version='0.1.0',                       # Package version
    description='Bitcoin node operations for Sallet projects',  # Short description
    long_description=open('_README.adoc').read(),  # Long description from the AsciiDoc file
    long_description_content_type='text/x-asciidoc',  # Content type for AsciiDoc
    author='Sziller',
    author_email='szillerke@gmail.com',
    url='https://github.com/sziller/_sallet_visor',
    license='MIT',                         # License type (choose the one you use)
    packages=['SalletNodePackage'],  # string-list of packages to be translated
    # packages=find_packages(),              # Automatically find all packages
    install_requires=[
        'requests>=2.32.0',  # Use the latest version of requests to fix the vulnerabilities
        'python-dotenv',
        'bitcoinlib'
    ],
    classifiers=[                          # Metadata for the package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',               # Specify the Python version requirement
)


# python3 setup.py sdist bdist_wheel
