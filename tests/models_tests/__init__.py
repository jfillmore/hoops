from tests import TestBase
from models import db as BaseDB
from tests import dbhelper
from models.core import Partner, Customer, User, Language
from config import OutputFormat


class ModelsTestBase(TestBase):
    db = BaseDB

    def populate_helper(self, lang=True, partner='test', customers=['test'], users=['test']):
        if lang:
            lang = self._add(Language(lang='en', name='English'))
        if partner:
            partner = self._add(Partner(language=lang, output_format=OutputFormat.JSON, name=partner))
        customers = [self._add(Customer(partner=partner, name=ident, my_identifier=ident)) for ident in customers]
        users = [self._add(User(partner=partner, customer=customers[0], my_identifier=ident)) for ident in users]

        return dict(lang=lang, partner=partner, customers=customers, users=users)

    def _add(self, obj):
        return dbhelper.add(obj, self.db)
