from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openexcept",
    version="0.1.0",
    author="OpenExcept",
    author_email="ai.observability.eng@gmail.com",
    description="Automatic exception grouping using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenExcept/OpenExcept",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi>=0.95.1",
        "openai==1.51.2",
        "qdrant-client==1.12.0",
        "requests==2.30.0",
        "sentence-transformers==3.2.0",
        "huggingface_hub>=0.20.0",
        "uvicorn==0.22.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "isort"],
    },
)
