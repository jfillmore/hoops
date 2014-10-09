
from test_config import OutputFormat
from test_models.core import Language, Partner, PartnerAPIKey
import random
from tests import dbhelper
import unittest
from sqlalchemy.exc import IntegrityError, OperationalError
from tests.models_tests import ModelsTestBase


class TestPartnerModels(ModelsTestBase, unittest.TestCase):

    def test_00_init(self):

        assert Partner
        assert PartnerAPIKey

    def test_01_populate(self):

        dbhelper.add(Language(lang='en', name='English'), self.db)
        dbhelper.add(Language(lang='en-US', name='English US'), self.db)
        lang_en = Language.get_one(lang='en')

        dbhelper.add(Partner(
            name='eNom', language_id=lang_en.id,
            output_format=OutputFormat.JSON, slug=None
        ), self.db)
        dbhelper.add(Partner(
            name='Dreamhost', language_id=lang_en.id,
            output_format=OutputFormat.JSON, slug='dream-host'
        ), self.db)

        dbhelper.add(PartnerAPIKey(
            consumer_key='d72f5f8a503e472847627f97a1519e',
            consumer_secret=nonce_generator(),
            token='token1',
            token_secret='token_secret1',
            partner_id=Partner.get_one(slug='enom').id, enabled=True
        ), self.db)

        dbhelper.add(PartnerAPIKey(
            consumer_key='465b0e4995a4b8e30727f20cf182c6',
            consumer_secret=nonce_generator(),
            token='token2',
            token_secret='token_secret2',
            partner_id=Partner.get_one(slug='dream-host').id,
            enabled=True
        ), self.db)

        assert Language.query.count() == 2,\
            'Language instances were not inserted'
        assert Partner.query.count() == 2,\
            'Partner instances were not inserted'
        assert PartnerAPIKey.query.count() == 2,\
            'PartnerAPIKey instances were not inserted'

    def test_02_repr(self):
        partner_api_key = PartnerAPIKey.query.limit(1).one()
        repr_string = partner_api_key.__repr__()
        assert 'PartnerAPIKey' in repr_string\
            and str(partner_api_key.id) in repr_string\
            and partner_api_key.consumer_key in repr_string, repr_string

    def test_05_default_for_enabled(self):
        dbhelper.add(
            PartnerAPIKey(
                consumer_key='55d7c2b1935bb931217ed7da9fd003',
                consumer_secret=nonce_generator(),
                token='token3',
                token_secret='token_secret3',
                partner_id=Partner.get_one(slug='dream-host').id
            ), self.db
        )

        assert PartnerAPIKey.get_one(
            consumer_key='55d7c2b1935bb931217ed7da9fd003'
        ).enabled is True, 'Default for enabled field not working'

    def test_06_error(self):
        #Non-unique consumer_key
        with self.assertRaises(IntegrityError):
            dbhelper.add(PartnerAPIKey(
                consumer_key='465b0e4995a4b8e30727f20cf182c6',
                consumer_secret=nonce_generator(),
                token='token4',
                token_secret='token_secret4',
                partner_id=Partner.get_one(slug='dream-host').id,
                enabled=True
            ), self.db)

        # No partner specified
        with self.assertRaises(OperationalError):
            dbhelper.add(
                PartnerAPIKey(
                    consumer_key='225162b53878eb69719f68b741d1e0',
                    consumer_secret=nonce_generator(),
                    token='token10',
                    token_secret='token_secret10',
                ), self.db
            )

        # No token specified
        with self.assertRaises(OperationalError):
            dbhelper.add(
                PartnerAPIKey(
                    consumer_key='225162b53878eb69719f68b741d1e0',
                    consumer_secret=nonce_generator(),
                    token_secret='token_secret10',
                    partner_id=Partner.get_one(slug='dream-host').id,
                ), self.db
            )

        # No token_secret specified
        with self.assertRaises(OperationalError):
            dbhelper.add(
                PartnerAPIKey(
                    consumer_key='225162b53878eb69719f68b741d1e0',
                    consumer_secret=nonce_generator(),
                    token='token10',
                    partner_id=Partner.get_one(slug='dream-host').id,
                ), self.db
            )

        # Invalid partner id
        with self.assertRaises(IntegrityError):
            dbhelper.add(PartnerAPIKey(
                consumer_key='225162b53878eb69719f68b741d1e0',
                consumer_secret=nonce_generator(),
                token='token5',
                token_secret='token_secret5',
                partner_id='81283712'
            ), self.db)

    def test_for_api_keys_relation(self):
        my_partner = Partner.query.first()
        my_api_keys = my_partner.api_keys
        assert my_partner.id == my_api_keys[0].partner.id


def nonce_generator(required_length=30):
    """ Method to generate a random string of specified length
    """
    rand_string = '%x' % random.randrange(16 ** required_length * 2)
    return rand_string[:required_length]
