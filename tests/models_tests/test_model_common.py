from flask import Flask
from tests.local import SQLALCHEMY_DATABASE_URI
import unittest
from tests import dbhelper
from models import db
from models.common import BaseModel, SluggableModel
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Integer, ForeignKey
import flask_sqlalchemy
import sqlalchemy.orm
import re
from tests import clear_database
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['TESTING'] = True


db.init_app(app)
db.app = app


class MyBaseModel(BaseModel):

    """Test model for BaseModel"""
    __tablename__ = 'test_base_model'
    __repr_fields__ = ('id', 'name',)

    name = Column(String(64), unique=True, nullable=False)
    multi = Column(String(64), unique=False, nullable=True)
    enabled = Column(Boolean, default=True)


class MySluggableModel(SluggableModel):

    """Test model for SluggableModel"""
    __tablename__ = 'test_sluggable_model'
    __slug_attribute__ = "name"
    __repr_fields__ = ('id', 'name',)

    name = Column(String(64), unique=True, nullable=False)
    slug = Column(String(64), unique=True, nullable=True)
    active = Column(Boolean, default=True)


class MyDisabledModel(BaseModel):

    """Test model for query_enabled disabled field"""
    __tablename__ = 'test_disabled'
    __repr_fields__ = ('id', 'name',)

    name = Column(String(64), unique=True, nullable=False)
    disabled = Column(Boolean, default=False)


class MyAlwaysActiveModel(BaseModel):

    """Test model for query_enabled disabled field"""
    __tablename__ = 'test_alays_enabled'
    __repr_fields__ = ('id', 'name',)

    name = Column(String(64), unique=True, nullable=False)


class MyAlwaysSuspendedModel(BaseModel):

    """Test model for query_all_except_suspended status field"""
    __tablename__ = 'test_always_suspended'
    __repr_fields__ = ('id', 'name', 'status')
    __props__ = 'name'

    name = Column(String(64), unique=True, nullable=False)
    status = Column(String(64), default='suspended', nullable=False)


class MyModelB(BaseModel):
    __tablename__ = 'mymodelb'

    mymodel_id = Column(Integer, ForeignKey('mymodel.id'), nullable=False)


class MyModel(BaseModel):
    __tablename__ = 'mymodel'
    __repr_fields__ = ('id', 'status', 'value')

    mymodelb = relationship(MyModelB, lazy='dynamic', backref=backref('mymodels'))
    status = Column(String(64), default='active', nullable=False)
    value = Column(String(10))


class TestCommonModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.create_all()
        clear_database(db)

    @classmethod
    def tearDownClass(cls):
        clear_database(db)

    def test_00_init(self):
        assert BaseModel
        assert SluggableModel
        assert MyBaseModel
        assert MySluggableModel

    def test_01_populate(self):
        # Add MyBaseModel instances
        db.session.add(MyBaseModel(name="Create Only Model"))
        db.session.add(MyBaseModel(name="Create Update Model"))
        db.session.commit()

        # Add MySluggableModel instances
        dbhelper.add(
            MySluggableModel(name='Test Model A', slug='test-model-aa'), db)
        dbhelper.add(MySluggableModel(name='Test Model B', slug=None), db)

        assert MyBaseModel.query.count() == 2
        assert MySluggableModel.query.count() == 2

    def test_02_repr_method(self):

        for myBaseModel in MyBaseModel.query.all():
            assert myBaseModel.name in str(myBaseModel)

        for testSlugModel in MySluggableModel.query.all():
            assert testSlugModel.name in str(testSlugModel)

    def test_03_slug_creation(self):

        testSlugModel = MySluggableModel.query.filter(
            MySluggableModel.name == 'Test Model A').first()

        assert testSlugModel.slug == 'test-model-aa'

        testSlugModel = MySluggableModel.query.filter(
            MySluggableModel.name == 'Test Model B').first()

        assert testSlugModel.slug == 'test-model-b'

    def test_04_created_at(self):

        for myBaseModel in MyBaseModel.query.all():
            assert myBaseModel.created_at is not None

        for testSlugModel in MySluggableModel.query.all():
            assert testSlugModel.created_at is not None

        myBaseModel = MyBaseModel.get_one(name="Create Only Model")
        testSlugModel = MySluggableModel.get_one(slug='test-model-aa')

        baseModelPrevCreatedAt = myBaseModel.created_at
        slugModelPrevCreatedAt = testSlugModel.created_at

        db.session.merge(
            MyBaseModel(id=myBaseModel.id, name='Created Only Model')
        )
        db.session.commit()

        item = MySluggableModel.get_one(slug='test-model-aa')
        item.name = 'Test Model A &'
        dbhelper.update(item, db)

        myBaseModel = MyBaseModel.get_one(name="Created Only Model")
        testSlugModel = MySluggableModel.get_one(slug='test-model-aa')

        assert baseModelPrevCreatedAt == myBaseModel.created_at
        assert slugModelPrevCreatedAt == testSlugModel.created_at

    def test_05_updated_at(self):

        for myBaseModel in MyBaseModel.query.all():
            assert myBaseModel.updated_at is not None

        for testSlugModel in MySluggableModel.query.all():
            assert testSlugModel.updated_at is not None

        myBaseModel = MyBaseModel.get_one(name="Create Update Model")
        testSlugModel = MySluggableModel.get_one(slug='test-model-b')

        baseModelPrevUpdatedAt = myBaseModel.updated_at
        slugModelPrevUpdatedAt = testSlugModel.updated_at

        time.sleep(1)
        db.session.merge(
            MyBaseModel(id=myBaseModel.id, name='Create Updated Model')
        )
        db.session.commit()

        item = MySluggableModel.get_one(slug='test-model-b')
        item.name = 'Test Model B &'
        dbhelper.update(item, db)

        myBaseModel = MyBaseModel.get_one(name="Create Updated Model")
        testSlugModel = MySluggableModel.get_one(slug='test-model-b')

        assert baseModelPrevUpdatedAt != myBaseModel.updated_at
        assert 'Test Model B &' == testSlugModel.name
        assert slugModelPrevUpdatedAt != testSlugModel.updated_at

    def test_06_get_one(self):
        assert MySluggableModel.get_one(slug='test-model-b')

        with self.assertRaises(NoResultFound):
            MySluggableModel.get_one(slug='xx=test-model-b')

        dbhelper.add(MyBaseModel(name='test1', multi='test1'), db)
        dbhelper.add(MyBaseModel(name='test2', multi='test1'), db)

        with self.assertRaises(MultipleResultsFound):
            MyBaseModel.get_one(multi='test1')

    def test_06_get_one_or_404(self):
        with app.app_context():
            assert MySluggableModel.get_one_or_404(slug='test-model-b')

            with self.assertRaises(NoResultFound):
                MySluggableModel.get_one_or_404(slug='xx=test-model-c')

    def test_07_query_active(self):
        assert MySluggableModel.query_active.count() == 2
        mysm = MySluggableModel.query.first()
        mysm.active = False
        dbhelper.update(mysm, db)
        assert MySluggableModel.query_active.count() == 1

        assert MyBaseModel.query_active.count() == 4
        mybm = MyBaseModel.query.first()
        mybm.enabled = False
        dbhelper.update(mybm, db)
        assert MyBaseModel.query_active.count() == 3

        dbhelper.add(MyDisabledModel(name='test'), db)
        assert MyDisabledModel.query_active.count() == 1
        dbhelper.add(MyDisabledModel(name='test2', disabled=True), db)
        assert MyDisabledModel.query_active.count() == 1

        dbhelper.add(MyAlwaysActiveModel(name='test'), db)
        assert MyAlwaysActiveModel.query_active.count() == 1

    def test_08_update_changes(self):
        dm = MyDisabledModel.get_one(name='test')
        dbhelper.update(dm, db, name='test3')
        with self.assertRaises(NoResultFound):
            dm = MyDisabledModel.get_one(name='test')
        dm = MyDisabledModel.get_one(name='test3')

    # TODO switch to utility once VC's code is merged
    def get_subclasses(self, klass):
        classes = klass.__subclasses__()
        return sum([[klass], sum([self.get_subclasses(k) for k in classes], [])], [])

    def test_09_relationships_are_flask_sqlalchemy(self):
        real_tables = filter(lambda c: hasattr(c, '__tablename__') and not re.match(r'^tests\.', c.__module__), self.get_subclasses(BaseModel))
        real_tables.extend([MyModelB])
        real_tables.extend([MyModel])

        skip = {
            "User": ["language"],
            "PartnerUser": ["name"],
        }

        for table in real_tables:
            o = table()
            for prop in filter(lambda p: not re.match(r'^_', p), dir(o)):

                skipme = skip.get(table.__name__)
                if skipme:
                    if prop in skipme:
                        continue

                try:
                    value = getattr(o, prop)
                    classval = getattr(table, prop)
                except Exception as e:
                    print "Failed for %s.%s: %s" % (table.__name__, prop, e)
                    raise e
                if isinstance(classval, sqlalchemy.orm.attributes.InstrumentedAttribute):
                    print '%s.%s is a InstrumentedAttribute' % (table.__name__, prop)
                    if hasattr(classval, 'property'):
                        if not isinstance(classval.property, sqlalchemy.orm.properties.RelationshipProperty):
                            continue

                        # Verify AppenderQueries can first_or_404 to verify they have flask_sqlalchemy behaviour
                        print "  property %s is a relationship" % classval.property
                        if isinstance(value, sqlalchemy.orm.dynamic.AppenderQuery):
                            if table in [MyModel, MyModelB]:
                                assert not hasattr(value, 'first_or_404'), "%s should not have first_or_404 method" % table

                            else:
                                assert hasattr(value, 'first_or_404'), \
                                    "Relationship %s does not have first_or_404 method: %s" % (
                                        classval.property,
                                        " - must use db.relationship instead of sqlalchemy.orm.relationship"
                                    )

                        # Verify backrefs have query_class == flask_sqlalchemy.BaseQuery if they are tuples (generated by backref routine)
                        if classval.property.backref and isinstance(classval.property.backref, tuple):
                            if table in [MyModel, MyModelB]:
                                assert not 'query_class' in classval.property.backref[1]
                            else:
                                assert classval.property.backref[1]['query_class'] == flask_sqlalchemy.BaseQuery

    def test_10_query_all_except_suspended(self):
        dbhelper.add(MyAlwaysSuspendedModel(name='test_query_active_or_suspended', status='suspended'), db)
        dbhelper.add(MyAlwaysSuspendedModel(name='test_query_active_or_suspended2', status='active'), db)
        assert MyAlwaysSuspendedModel.query_all_except_suspended.count() == 1, "Should only have one not-suspended item"

    def test_11_for_props_in_models_common(self):
        MySluggableModel.__props__ = ['name']
        data = dbhelper.add(MySluggableModel(name='test_props'), db).to_json()
        assert data['name'] == "test_props", "Data not inserted correctly"
        assert MySluggableModel.query.count() == 3

    def test_apply_active_filter(self):
        '''Tests to ensure that _apply_active_filter checks the status column too (via query_active)'''
        dbhelper.add(MyModel(status='deleted', value=1), db)
        dbhelper.add(MyModel(status='active', value=2), db)
        c = MyModel.query_active.first()
        assert c.status == 'active'
        c = MyModel.query_active.filter_by(value=1).first()
        assert c is None

    def test_query_active_or_suspended_with_query(self):
        for item in MyModel.query:
            dbhelper.delete(item, db)
        dbhelper.add(MyModel(status='active', value=1), db)
        dbhelper.add(MyModel(status='suspended', value=2), db)
        dbhelper.add(MyModel(status='deleted', value=3), db)
        assert MyModel.query_active_or_suspended.count() == 2, MyModel.query_active_or_suspended.count()
