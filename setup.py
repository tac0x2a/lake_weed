from setuptools import setup


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="lakeweed",
    version="1.2.2",
    author="TAC",
    author_email="tac@tac42.net",
    description=("Elastic parser for data-like string, JSON, JSON Lines, and CSV to RDB record"),
    license="MIT",
    keywords="json jsonline csv rabbitmq amqp clickhouse",
    url="https://github.com/tac0x2a/lake_weed",
    packages=['lakeweed'],
    install_requires=_requires_from_file('requirements.txt')
)
