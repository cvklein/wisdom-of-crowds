pytest --junitxml=.reports/junit.xml
genbadge tests -v -i .reports/junit.xml -o .reports/tests-badge.svg
coverage run -m pytest
coverage xml -o .reports/coverage.xml ../src/wisdom_of_crowds.py
genbadge coverage -v -i .reports/coverage.xml -o .reports/coverage-badge.svg