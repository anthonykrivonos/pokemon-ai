from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("./requirements.txt") as req_file:
    requirements = req_file.read()

setup_requirements, test_requirements = [], []
setup(
    name='pokemon_ai',
    version='0.0.1',
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests"]),
    url='https://github.com/anthonykrivonos/pokemon-ai',
    include_package_data=True,
    test_suite="tests",
    tests_require=test_requirements,
    license='',
    author='anthonykrivonos',
    author_email='',
    description='',
    install_requires=requirements,
    setup_requires=setup_requirements,
    long_description=readme,
    zip_safe=False,
)
