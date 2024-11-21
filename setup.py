from setuptools import find_packages, setup

with open("README.md", "r") as f:
    l_description = f.read()
    
setup(
    name="temmies",
    version="1.2.1",
    packages=find_packages(),
    description="A wrapper for the Themis website",
    long_description=l_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Code-For-Groningen/temmies",
    author="Boyan K.",
    author_email="boyan@confest.im",
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "requests",
        "lxml",
        "beautifulsoup4",
        "keyring"
    ],
    python_requires=">=3.9",
)