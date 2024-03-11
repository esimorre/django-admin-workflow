try:
    from apptest.models import MyTestModel
except RuntimeError:
    print("Execute test with --settings django_admin_workflow.test.settings")
    print("or add apptest in settings (maybe required in debug mode).")

from .test.test_base import *
