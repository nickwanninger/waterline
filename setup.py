from setuptools import find_packages, setup

setup(
    name="waterline",
    packages=find_packages(),
    version="0.1.12",
    description="A unified LLVM benchmark pipeliner",
    author="Nick Wanninger",
    license="MIT",
    install_requires=["rich", "requests", "pandas"],
    include_package_data=True,
    package_data={"": ["waterline"]},
)
