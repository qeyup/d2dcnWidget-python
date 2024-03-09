#!/usr/bin/env python3


import d2dcnWidget
import setuptools


if __name__ == '__main__':
    setuptools.setup(
        name = 'd2dcnWidget',
        version = d2dcnWidget.version,
        packages = ["d2dcnWidget"],
        entry_points={
            'console_scripts': [
                'd2dcnGUI=d2dcnWidget.d2dcnGUI:main'
            ],
        },
        install_requires = [
            "d2dcn",
            "PyQt5"
        ],
        author = "Javier Moreno Garcia",
        author_email = "jgmore@gmail.com",
        description = "",
        long_description_content_type = "text/markdown",
        long_description = "",
        url = "https://github.com/qeyup/d2dcnWidget-python"
    )
