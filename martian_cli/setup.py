import setuptools

setuptools.setup(
    name="martian_cli",
    version="0.0.1",
    author="Marcus Kinsella",
    author_email="mkinsella@chanzuckerberg.com",
    packages=["martian_cli"],
    install_requires=["pyparsing"],
    entry_points={
        'console_scripts': ["martian=martian_cli.cli:main"]
        }
)
