import setuptools

from scraper import __version__


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ultimate-facebook-scraper",
    version=__version__,
    author="Haris Muneer",
    author_email="haris.muneer@conradlabs.com",
    license="MIT",
    keywords="Facebook Scraper",
    description="A bot which scrapes almost everything about a Facebook user's profile",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/harismuneer/Ultimate-Facebook-Scraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    extras_require={"dev": ["black", "twine", "wheel"],},
    install_requires=["selenium==3.141.0", "pyyaml", "webdriver_manager"],
    entry_points={
        "console_scripts": ["ultimate-facebook-scraper=scraper.__main__:scraper",],
    },
)
