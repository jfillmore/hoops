from tests import TestBase, config_file, db_config
from tests import dbhelper
from test_models.core import Partner, Customer, User, Language
from hoops.utils import OutputFormat
from hoops import create_api


class ModelsTestBase(TestBase):

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

    @classmethod
    def get_app(cls):
        app, cls.db = create_api(db_config=db_config,
                                 config_file=config_file,
                                 app_name='hoops',
                                 flask_conf={'DEBUG': True,
                                             'ENVIRONMENT_NAME': 'test'})
        return app
