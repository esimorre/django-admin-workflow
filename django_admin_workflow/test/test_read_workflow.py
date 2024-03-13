from unittest import TestCase

import tomli


class ReadWorkflow(TestCase):
    def test_read_py(self):
        dic = None
        with open("apptest/workflow.py", "r", encoding="utf-8") as f:
            wf = f.read()
            dic = eval(wf)
        self.assertTrue('clients' in dic)
        print (dic)

    def test_read_toml(self):
        dic = None
        with open("apptest/workflow.toml", "rb") as f:
            dic = tomli.load(f)
        self.assertTrue('clients' in dic)
        print (dic)
