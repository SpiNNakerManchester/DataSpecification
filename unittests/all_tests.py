
"""
runs all spinn front end common tests scripts
"""
import unittest

testmodules = ['test_data_spec_executor', 'test_data_spec_executor_functions',
               'test_data_spec_generator', 'test_enums',
               'test_file_data_reader', 'test_file_data_writer',
               'test_memory_region_collection']

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)