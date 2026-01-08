"""Setup for games XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.
    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name="edx-games",
    version="1.0.8",
    description="Interactive games XBlock for Open edX - Create flashcards and matching games with image support",
    author="edX",
    author_email="edx@edx.org",
    url="https://github.com/edx/gamesxblock",
    license="AGPL v3",
    packages=[
        "games",
        "games.handlers",
    ],
    install_requires=[
        "XBlock>=1.2.0",
        "web-fragments>=0.3.0",
        "Django>=2.2",
        "django-waffle==5.0.0",
        "edx-toggles==5.4.1",
        "cryptography>=3.4.8",
    ],
    entry_points={
        "xblock.v1": [
            "games = games:GamesXBlock",
        ]
    },
    package_data=package_data("games", ["static", "locale"]),
)
