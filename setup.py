from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="VLCYT",
    version="1.8",  # update VLCYT version in requirements as well
    description="Stream your YouTube playlist in VLC behind the scenes from the command line.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Timothy Hill Jr",
    license="MIT",
    url="https://github.com/hillt03/VLCYT",
    keywords="youtube vlc stream playlist",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.3",
        "pafy>=0.5.5",
        "python-vlc>=3.0.7110",
        "youtube-dl>=2019.11.28",
        "pyperclip>=1.7.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
)
