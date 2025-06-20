import unittest
import os
import sys

if __name__ == "__main__":
    print('CWD:', os.getcwd())
    print('Files in /app:', os.listdir('.'))
    if os.path.exists('tests'):
        print('Files in /app/tests:', os.listdir('tests'))
    else:
        print('tests directory not found!')
    sys.path.insert(0, os.getcwd())  # Ensure current dir is in sys.path
    loader = unittest.TestLoader()
    # Use top_level_dir to help Python find the package
    suite = loader.discover(start_dir="tests", top_level_dir=".")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    # Exit with appropriate code for CI/CD
    exit_code = 0 if result.wasSuccessful() else 1
    os._exit(exit_code)
