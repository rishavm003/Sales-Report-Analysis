from setuptools import setup, find_packages

setup(
    name='sales-dashboard',
    version='0.1.0',
    description='A comprehensive sales analysis dashboard with data visualization capabilities',
    author='Rishav',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'pandas',
        'plotly',
        'sqlite3',
        'openpyxl'
    ],
    python_requires='>=3.8',
)