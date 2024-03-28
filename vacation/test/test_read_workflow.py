from unittest import TestCase

import tomli
from django.contrib.auth.models import Group


class ReadWorkflow(TestCase):
    def test1_read_toml(self):
        dic = {}
        with open("vacation/workflow.toml", "rb") as f:
            dic = tomli.load(f)
        self.assertTrue('employees' in dic)
        for data in dic.values():
            if 'filter' in data and data['filter'].strip().startswith("lambda"):
                data['filter'] = eval(data['filter'])
        return dic

    def test2_import_workflow(self):
        dic_workflow = self.test1_read_toml()
        perms, status = [], []
        for gname, data in dic_workflow.items():
            g, c = Group.objects.get_or_create(name=gname)
            for key, content in data.items():
                if key in ('filter', 'creation'): continue
                status.append(key)
                if 'actions' in content:
                    for action in content['actions']:
                        if len(action) > 2: status.append(action[2])

        print(perms, status)
