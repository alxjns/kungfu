import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kungfu",
    description="Kungfu helps you create Karate tests from OpenApi specs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
