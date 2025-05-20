from setuptools import setup, find_packages

setup(
    name="namecheap-mcp",
    version="0.0.1",
    description="MCP Server for Namecheap API integration",
    author="Praful Mathur",
    author_email="praful@aionthebeach.com",
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "mcp[cli]>=1.9.0"
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'namecheap-mcp=src.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
