from tests.models_tests import ModelsTestBase
from models.core import Language
from tests import dbhelper
from sqlalchemy.exc import IntegrityError


class TestLanguageModel(ModelsTestBase):

    def test_00_init(self):
        assert Language

    def test_01_populate(self):
        dbhelper.add(Language(lang='en', name='English'), self.db)
        dbhelper.add(Language(lang='en-us', name='English US'), self.db)
        dbhelper.add(Language(lang='es', name='Espanol'), self.db)
        dbhelper.add(Language(lang='fr', name='French'), self.db)

        # Duplicate entry
        try:
            dbhelper.add(Language(lang='fr', name='French'), self.db)
            assert False, 'Expected IntegrityError'
        except IntegrityError:
            pass

        assert Language.query.count() == 4

    def test_02_repr_method(self):
        languages = Language.query.all()

        for language in languages:
            assert str(language.id) in str(language)
            assert language.lang in str(language)
            assert language.name in str(language)

    def test_04_languages_lang_name_present(self):
        for language in Language.query.all():
            assert (language.lang is not None and language.lang is not '')
            assert (language.name is not None and language.name is not '')

    def test_05_languages_unique(self):
        assert Language.query.filter(Language.lang == 'en').count() == 1
        assert Language.query.filter(Language.lang == 'en').first().name == 'English'


