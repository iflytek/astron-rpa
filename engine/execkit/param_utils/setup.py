from setuptools import find_packages, setup

version = "1.0.5"

packages = find_packages("src")
console_scripts = []
package_data = {}
install_requires = []
extras_require = {}


def readme():
    with open("README.md", encoding="utf-8") as f:
        content = f.read()
    return content


setup(
    name="rpa-param-utils",
    version=version,
    author="ybcao4",
    author_email="ybcao4@iflytek.com",
    description="rpa-param-utils.",
    long_description=readme(),
    url="http://iflytek.com/",
    license="Apache2.0",
    packages=packages,
    package_data=package_data,
    package_dir={"": "src"},
    include_package_data=False,
    install_requires=install_requires,
    extras_require=extras_require,
    python_requires=">=3.7",
    entry_points={"console_scripts": console_scripts},
)
