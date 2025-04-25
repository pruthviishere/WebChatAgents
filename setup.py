from setuptools import setup, find_packages

setup(
    name="webchat_agents",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "requests",
        "beautifulsoup4",
        "python-dotenv",
        "pytest",
        "pytest-asyncio",
    ],
    python_requires=">=3.8",
) 