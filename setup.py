from setuptools import setup, find_packages
import cbdocragdemo
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='cbdocragdemo',
    version=cbdocragdemo.__version__,
    packages=find_packages(exclude=['tests']),
    url='https://github.com/mminichino/cb-docs-rag-demo',
    license='MIT License',
    author='Michael Minichino',
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'demo_prep = cbdocragdemo.demo_prep:main',
            'demo_run = cbdocragdemo.streamlit_exec:main',
            'vector_load = cbdocragdemo.vector_load:main',
            'data_load = cbdocragdemo.data_load:main',
            'data_export = cbdocragdemo.data_export:main'
        ]
    },
    install_requires=[
        "couchbase>=4.2.1",
        "streamlit>=1.32.2",
        "httpx>=0.27.0",
        "langchain>=0.1.13",
        "langchain-community>=0.0.29",
        "langchain-openai>=0.1.0",
        "tiktoken>=0.6.0",
        "pypdf>=4.1.0",
        "requests>=2.31.0",
        "cbcmgr>=2.2.40",
        "tqdm>=4.66.2",
        "lxml>=5.1.1",
        "jq>=1.7.0",
        "beautifulsoup4>=4.12.3",
        "certifi>=2024.2.2",
        "python-certifi-win32>=1.6.1",
        "pillow>=10.2.0",
        "watchdog>=4.0.0"
    ],
    author_email='info@unix.us.com',
    description='Couchbase RAG Demo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=["couchbase", "vector", "demo"],
    classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Topic :: Software Development :: Libraries",
          "Topic :: Software Development :: Libraries :: Python Modules"],
)
