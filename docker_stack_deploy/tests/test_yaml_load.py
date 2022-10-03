from unittest import TestCase
import yaml

DOUBLE_DOLLAR = """
prom2teams:
    image: idealista/prom2teams:3.3.0
    entrypoint: /bin/sh -c "python /opt/prom2teams/replace_config.py && exec prom2teams --loglevel $$PROM2TEAMS_LOGLEVEL"
"""

class YAMLDollarTest(TestCase):
    def test_double_dollar(self) -> None:
        parsed = yaml.load(DOUBLE_DOLLAR, yaml.FullLoader)