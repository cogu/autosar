import os, sys
import unittest
import shutil
import time

class ARXMLTestClass(unittest.TestCase):
    
    output_dir = 'derived'

    @classmethod
    def setUpClass(cls):
        output_dir_full = os.path.join(os.path.dirname(__file__), cls.output_dir)
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
            time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        output_dir_full = os.path.join(os.path.dirname(__file__), cls.output_dir)
        os.rmdir(output_dir_full)

    def save_and_check(self, ws, expected_file, generated_file, filters = None, force_copy=False):
        expected_path = os.path.join(os.path.dirname(__file__), expected_file)
        generated_path = os.path.join(os.path.dirname(__file__), generated_file)
        ws.saveXML(generated_path, filters=filters)
        if force_copy:
            shutil.copyfile(generated_path, expected_path)
        with open (expected_path, "r") as fp:
            expected_text=fp.read()
        with open (generated_path, "r") as fp:
            generated_text=fp.read()
        self.assertEqual(expected_text, generated_text)
        os.remove(generated_path)
