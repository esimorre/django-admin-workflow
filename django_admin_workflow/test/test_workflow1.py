from django.test import TestCase
from .helpers import *

class TestCase(TestCase):

    def test1(self):
        create_space("Dep1", users=('cli1', 'cli1b'), role_add='clients')
        create_space("Dep2", users=('cli2', 'cli2b'), role_add='clients')

        create_states(("accepted", "valid", "published",))
        create_roles(("submiter", "validator", "publisher"))
        create_su()

        rep = self.client.get("/login/")
        self.assertEqual(rep.status_code, 200)
        rep = self.client.post("/login/", {"name": "admin", "passwd": "admin"})
        rep = self.client.post("/logout/")
        rep = self.client.post("/login/", {"name": "cli1", "passwd": "cli1"})
        rep = self.client.post("/logout/")
        self.assertEqual(rep.status_code, 302)

        rep = self.client.post("/login/", {"name": "admin", "passwd": "BADXXXXXXX"})
        self.assertEqual(rep.context_data['title'], "Connexion")
