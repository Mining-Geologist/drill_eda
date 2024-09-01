from setuptools import setup, find_packages

setup(
    name="DrillEda",
    version="0.1.4",
    description="A package for exploratory data analysis of drillhole data.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Mining Geologist",
    author_email="geologytrainings@gmail.com",
    url="https://github.com/Mining-Geologist/drill_eda",  # Update with your repository URL
    py_modules=["DrillEda"],
    install_requires=[
        "pandas==1.4.2",
        "matplotlib==3.5.2",
        "numpy==1.26.4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
