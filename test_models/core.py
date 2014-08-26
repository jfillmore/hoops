
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, UniqueConstraint, Numeric
import re
from flask_login import UserMixin
from jetlaunch_common.util import random_key_generator
from test_models.common import BaseModel, SluggableModel, HashableModel
from test_models import db
from test_models.basekit import BaseKitSite


class Partner(SluggableModel):
    """Partner details."""

    __tablename__ = 'partner'
    __slug_attribute__ = "name"
    __repr_fields__ = ('id', 'name', )

    name = Column(String(64), unique=True, nullable=False)
    slug = Column(String(64), unique=True, nullable=False)
    language_id = Column(Integer, ForeignKey('languages.id'), nullable=False)
    output_format = Column(String(64), nullable=False)
    enabled = Column(Boolean, default=True)

    language = db.relationship("Language")
    customers = db.relationship("Customer", lazy='dynamic', backref="partner")
    users = db.relationship("User", lazy='dynamic', backref="partner")
    domains = db.relationship("Domain", lazy='dynamic', backref="partner")
    basekit_brands = db.relationship("BaseKitBrand", backref="partner")
    api_keys = db.relationship('PartnerAPIKey', lazy='dynamic', backref='partner')
    packages = db.relationship('Package', lazy='dynamic', backref='partner')
    partner_users = db.relationship("PartnerUser", lazy='dynamic', backref="partner")

    def generate_api_key(self, consumer_key, **kwargs):
        new = PartnerAPIKey(consumer_key=consumer_key, partner=self, **kwargs)
        for field in ['consumer_secret', 'token', 'token_secret']:
            if not getattr(new, field):
                setattr(new, field, random_key_generator())
        return new


class PartnerAPIKey(BaseModel):
    """API keys for existing partners."""

    __tablename__ = 'partner_api_key'
    __repr_fields__ = ('id', 'consumer_key', )

    consumer_key = Column(String(255), nullable=False, unique=True)
    consumer_secret = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False)
    token_secret = Column(String(255), nullable=False)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)


class Customer(BaseModel):

    """Customer details."""
    __tablename__ = 'customer'
    __repr_fields__ = ('id', 'name',)
    __table_args__ = (
        UniqueConstraint('partner_id', 'my_identifier'),
    )

    name = Column(String(64))
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    status = Column(String(64), default='active', server_default='active', nullable=False)
    my_identifier = Column(String(64))

    _valid_status_values = ('active', 'inactive', 'disabled', 'suspended', 'deleted')

    users = db.relationship("User", lazy='dynamic', backref='customer')

    @classmethod
    def _apply_active_filter(cls, query):
        return query.filter(cls.status == 'active')

    @classmethod
    def get_service_classes(cls):
        return (BaseKitSite,)

    def get_active_services(self):
        '''Returns an array of query handles for all services that have ever been provisioned for a customer'''
        return [klass.get_for_customer_id(customer_id=self.id) for klass in self.get_service_classes()]

    def count_active_services(self):
        return sum(item.count() for item in self.get_active_services())

    def updates_permitted(self, **kwargs):
        if self.status in ('deleted', 'disabled'):
            return False
        # TODO: Consider whether we wish to permit changing details when suspended
        return True

    @classmethod
    def is_valid_status_transition(self, from_status, to_status):
        if from_status == to_status:
            return True
        if from_status == 'deleted':
            return False
        if from_status == 'disabled':
            return False
        if to_status == 'disabled':
            return False
        return True


class User(HashableModel):

    """User details."""
    __tablename__ = 'user'
    __hash_attribute__ = 'password'
    __repr_fields__ = ('id', 'firstname', 'lastname')
    __table_args__ = (
        UniqueConstraint('partner_id', 'email'),
        UniqueConstraint('partner_id', 'my_identifier')
    )

    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    language_id = Column(Integer, ForeignKey('languages.id'), unique=False, nullable=False)
    status = Column(String(64), default='active',
                    server_default='active', nullable=False)
    firstname = Column(String(64))
    lastname = Column(String(64))
    email = Column(String(120))
    password = Column(String(255), nullable=True)
    role = Column(String(32), default='owner', server_default='owner')
    my_identifier = Column(String(64))

    basekit_users = db.relationship("BaseKitUser", lazy='dynamic', backref="user")
    basekit_sites = db.relationship("BaseKitSite", lazy='dynamic', backref="user")

    def to_json(self, *args, **kwargs):
        out = super(User, self).to_json(*args, **kwargs)
        del out['language_id']
        out['language'] = Language.query.get(self.language_id).lang
        return out

    @classmethod
    def _apply_active_filter(cls, query):
        return query.filter(cls.status == 'active')

    def updates_permitted(self, **kwargs):
        if self.status in ('deleted', 'disabled'):
            return False
        if not self.customer.updates_permitted():
            return False
        return True


class Language(BaseModel):
    """Language supported by the site."""
    __tablename__ = 'languages'
    __repr_fields__ = ('id', 'lang', 'name')

    lang = Column(String(length=8), unique=True, nullable=False)
    name = Column(String(length=80), unique=True, nullable=False)
    active = Column(Integer, default=1, nullable=False)

    users = db.relationship(User, lazy='dynamic', backref='language')

    def to_json(self, *args, **kwargs):

        return {
            "lang": self.lang,
            "name": self.name
        }


class Service(SluggableModel):
    """Service available for various Packages."""
    __tablename__ = 'service'
    __slug_attribute__ = "name"

    name = Column(String(64), nullable=False)
    provisioning_enabled = Column(Boolean, default=True, nullable=False)
    slug = Column(String(64), unique=True, nullable=False)


class PackageServiceParam(BaseModel):
    """Package service parameters."""

    __tablename__ = 'package_service_param'
    __table_args__ = (
        UniqueConstraint('package_service_id', 'param_name'),
    )

    package_service_id = Column(Integer, ForeignKey('package_service.id'), nullable=False)
    param_name = Column(String(64), nullable=False)
    param_value = Column(String(255))


class PackageService(BaseModel):
    """Package services."""

    __tablename__ = 'package_service'

    package_id = Column(Integer, ForeignKey('package.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)

    service = db.relationship(Service)
    params = db.relationship(PackageServiceParam, lazy='dynamic', backref='package_service')

    def to_json(self, *args, **kwargs):

        def tidy_param_value(value):
            if value is None:
                return value
            if unicode(value).isdecimal():
                return int(value)
            if re.match(r'^\d+\.\d+$', value):
                return float(value)
            return value

        out = {"service": self.service.slug}
        out.update({item.param_name: tidy_param_value(item.param_value) for item in self.params})
        return out


class Package(BaseModel):
    """Package details."""

    __tablename__ = 'package'
    __repr_fields__ = ('id', 'name', )
    __table_args__ = (
        UniqueConstraint('partner_id', 'name'),
    )

    name = Column(String(64), unique=False, nullable=False)
    enabled = Column(Boolean, default=True)
    description = Column(Text(64), nullable=False)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)

    package_services = db.relationship(PackageService, lazy='dynamic', backref='package')

    def to_json(self, *args, **kwargs):
        out = super(Package, self).to_json(*args, **kwargs)
        out['services'] = [
            service.to_json() for service in self.package_services
        ]
        return out


class CustomerPackage(BaseModel):
    """Join table between TLDs and Categories."""
    __tablename__ = 'customer_package'
    __table_args__ = (
        UniqueConstraint('package_id', 'customer_id'),
    )
    package_id = Column(Integer, ForeignKey('package.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    status = Column(String(64), default='active', server_default='active', nullable=False)

    package = db.relationship(Package, backref=db.backref('customerpackages', lazy='dynamic'))
    customer = db.relationship(Customer, backref=db.backref('packages', lazy='dynamic'))
    # TO DO : Refactor this using http://docs.sqlalchemy.org/en/rel_0_8/orm/db.relationships.html#many-to-many

    def to_json(self, *args, **kwargs):
        ret = self.package.to_json(*args, **kwargs)
        if 'enabled' in ret:
            del ret['enabled']
        if 'partner_id' in ret:
            del ret['partner_id']
        ret['status'] = self.status
        ret['created_at'] = unicode(self.created_at)
        ret['updated_at'] = unicode(self.updated_at)
        return ret

    def updates_permitted(self, **kwargs):
        if not self.customer.updates_permitted():
            return False
        return True


class PartnerUser(HashableModel, UserMixin):
    """Partner User details."""
    __tablename__ = 'partner_user'
    __hash_attribute__ = 'password'
    __repr_fields__ = ('id', 'firstname', 'lastname')
    __table_args__ = (
        UniqueConstraint('partner_id', 'email'),
        UniqueConstraint('partner_id', 'my_identifier')
    )

    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    status = Column(String(64), default='active',
                    server_default='active', nullable=False)
    firstname = Column(String(64))
    lastname = Column(String(64))
    email = Column(String(120))
    password = Column(String(255), nullable=True)
    my_identifier = Column(String(64))

    @property
    def name(self):
        return self.firstname + ' ' + self.lastname

    def is_active(self):
        '''Returns True if this is an active partner user - in addition to being authenticated,
        they also have activated their account, not been suspended, or any condition your application
        has for rejecting an account.
        Inactive accounts may not log in (without being forced of course).'''
        if self.status == 'active':
            return True


class PasswordChangeRequests(HashableModel):
    __tablename__ = 'password_change_requests'
    __hash_attribute__ = 'my_identifier'
    __repr_fields__ = ('id')

    my_identifier = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('partner_user.id'), nullable=False)


class Domain(BaseModel):

    """
    Domain name registered for this customer
    """
    __tablename__ = 'domain'
    __repr_fields__ = ('domain')

    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)  # sld.tld
    domain_extension = Column(String(64), nullable=False)  # tld
    order_ref = Column(String(64))
    total_amount = Column(Numeric(9, 2))
    # virtual fields, managed via enom API
    # - name_server
    # - host_ip
    # - contacts
    #       - admin
    #       - tech
    #       - billing
    #       - registrant
