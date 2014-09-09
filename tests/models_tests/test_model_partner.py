
import unittest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from test_config import OutputFormat
from tests import dbhelper
from test_models.core import Partner, Language
from tests.models_tests import ModelsTestBase
import time


class TestPartnerModel(ModelsTestBase, unittest.TestCase):

    def test_01_populate(self):
        dbhelper.add(Language(lang='en', name='English'), self.db)
        dbhelper.add(Language(lang='fr', name='French'), self.db)

        dbhelper.add(Partner(
            name='eNom2', language_id=Language.get_one(lang='en').id,
            output_format=OutputFormat.JSON, slug=None
        ), self.db)
        # Custom slug
        dbhelper.add(Partner(
            name='Dreamhost', language_id=Language.get_one(lang='fr').id,
            output_format=OutputFormat.JSON, slug='dream-host'
        ), self.db)

        #Disabled partner
        dbhelper.add(Partner(
            name='Disabled Partner', language_id=Language.get_one(lang='fr').id,
            output_format=OutputFormat.JSON, enabled=False
        ), self.db)

        assert Partner.query.count() == 3, 'Found %d instances.' % (Partner.query.count())

    def test_02_repr(self):
        for partner in Partner.query_active:
            repr_string = partner.__repr__()
            assert 'Partner' in repr_string and str(partner.id) in repr_string \
                and partner.name in repr_string, \
                'Partner repr method is not working'

    def test_03_created_at(self):

        for partner in Partner.query.all():
            assert partner.created_at is not None

        partner = Partner.get_one(slug='enom2')

        partnerPrevCreatedAt = partner.created_at

        dbhelper.update(partner, self.db, name='Enom&')

        partner = Partner.get_one(slug='enom2')

        assert partnerPrevCreatedAt == partner.created_at

    def test_04_updated_at(self):

        for partner in Partner.query.all():
            assert partner.updated_at is not None

        partner = Partner.get_one(slug='dream-host')

        partnerPrevUpdatedAt = partner.updated_at
        time.sleep(1)
        dbhelper.update(partner, self.db, output_format=OutputFormat.XML)

        partner = Partner.get_one(slug='dream-host')

        assert partnerPrevUpdatedAt != partner.updated_at

    def test_05_slug(self):
        #Fetch by auto-generated slug
        assert Partner.get_one(slug='enom2') is not None, 'Slug auto-generation failed'

        # Fetch by custom slug
        partner = Partner.get_one(slug='dream-host')

        assert partner is not None and partner.name == 'Dreamhost',\
            'Custom slug has been overriden in Partner'

        en_lang = Language.get_one(lang='en')

        # Duplicate slug
        with self.assertRaises(IntegrityError):
            dbhelper.add(Partner(
                name='eNom&',
                language_id=en_lang.id,
                output_format=OutputFormat.JSON,
                slug=None
            ), self.db)

    def test_06_language(self):

        with self.assertRaises(IntegrityError):
            dbhelper.add(Partner(
                name='eNom&#', language_id=109281, output_format=OutputFormat.JSON, slug=None
            ), self.db)

    @unittest.skip('field validations not yet implemented')
    def test_07_output_format(self):
        en_lang = Language.get_one(lang='en')

        try:
            #Invalid output_format
            dbhelper.add(Partner(
                name='eNom&#', language_id=en_lang.id, output_format='txt', slug=None
            ), self.db)
        except AssertionError:
            pass

        #assert 'Invalid output_format' in ae, 'Invalid output_format accepted'

    def test_08_update(self):
        with self.assertRaises(IntegrityError):
            dbhelper.update(Partner.get_one(slug='enom2'), self.db, name='Dreamhost')

        fr_lang = Language.get_one(lang='fr')
        with self.assertRaises(NoResultFound):
            dbhelper.update(Partner.get_one(slug='enom-123'), self.db, language_id=fr_lang.id)

        dbhelper.update(Partner.get_one(slug='enom2'), self.db, language_id=fr_lang.id)
        partner = Partner.get_one(slug='enom2')

        assert partner.language_id == fr_lang.id, 'Partner update method not working'

    def test_09_check_enabled(self):

        assert Partner.query_active.count() == 2, 'Disabled partners included get_active method. %d ' % Partner.get_active().count()
        assert Partner.get_one(slug='enom2').enabled is True, 'Partner enabled field default not set'
        assert Partner.get_one(slug='disabled-partner').enabled is False, 'Partner enabled field overriden'
