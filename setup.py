from setuptools import setup

setup(
    name="mcorepv",
    description="Provision manticore jobs locally or remotely",
    version="0.1.0",
    packages=["mcorepv"],
    author="pwang00",
    python_requires=">=3.6",
    install_requires=["manticore", "ansible>=2.8", "prompt-toolkit"],
    entry_points={"console_scripts": ["mcorepv = mcorepv.__main__:main"]},
)
