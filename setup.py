from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='union_erpnext',
    version=version,
    description='Union Erpnext Extensions',
    author='laurence@union.ph',
    author_email='laurence@union.ph',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
