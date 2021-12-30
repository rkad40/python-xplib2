import coverage

print(
r"""
 _____         _    __  ______  _     ___ ____
|_   _|__  ___| |_  \ \/ /  _ \| |   |_ _| __ )
  | |/ _ \/ __| __|  \  /| |_) | |    | ||  _ \
  | |  __/\__ \ |_   /  \|  __/| |___ | || |_) |
  |_|\___||___/\__| /_/\_\_|   |_____|___|____/

""")


cov = None
run_coverage = True
if run_coverage:
    cov = coverage.coverage(branch=True, include=r".\*")
    cov.start()

import unittest
tests = unittest.TestLoader().discover(r'test')
unittest.TextTestRunner(verbosity=2).run(tests)
print()

if run_coverage:
    cov.stop()
    cov.save()
    print('Coverage Summary:')
    cov.report()
    cov.html_report(directory="./test/reports")
    cov.erase()
