
from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy import ForeignKey, UniqueConstraint

from hoops.utils import SluggableModel, BaseModel
from hoops import db


class BaseKitCluster(SluggableModel):

    """BaseKitCluster details."""
    __tablename__ = 'basekit_cluster'
    __slug_attribute__ = "name"

    name = Column(String(64), nullable=True)
    slug = Column(String(64), unique=True, nullable=False)
    description = Column(Text(64), nullable=True)
    api_url = Column(String(255), nullable=True)
    provisioning_enabled = Column(Boolean, default=True, nullable=False)

    basekit_nodes = db.relationship("BaseKitNode", backref="cluster", lazy='dynamic')
    basekit_brands = db.relationship("BaseKitBrand", backref="cluster", lazy='dynamic')
    basekit_packages = db.relationship("BaseKitPackage", backref="cluster", lazy='dynamic')

    def __repr__(self):
        return "<BaseKitCluster('%d', '%s')>" % (self.id, self.slug)


class BaseKitNode(BaseModel):

    """BaseKitNode details."""
    __tablename__ = 'basekit_node'

    cluster_id = Column(Integer, ForeignKey('basekit_cluster.id'), nullable=False)
    cname = Column(String(255), nullable=True)
    ip = Column(String(255), nullable=True)
    provisioning_enabled = Column(Boolean, default=True, nullable=False)
    instance_count = Column(Integer, nullable=False)
    max_instances = Column(Integer, nullable=False)

    def __repr__(self):
        return "<BaseKitNode('%d', '%s')>" % (self.id, self.cname)


class BaseKitBrand(SluggableModel):

    """BaseKitBrand details."""
    __tablename__ = 'basekit_brand'
    __slug_attribute__ = "name"

    name = Column(String(64), nullable=True)
    slug = Column(String(64), unique=True, nullable=False)
    cluster_id = Column(Integer, ForeignKey('basekit_cluster.id'), nullable=False)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=False)
    provisioning_enabled = Column(Boolean, default=True, nullable=False)
    bk_brand_id = Column(String(64), nullable=False)
    default_domain = Column(String(64), nullable=False)
    oauth_consumer_key = Column(String(128), nullable=True)
    oauth_consumer_secret = Column(String(255), nullable=True)
    oauth_token = Column(String(255), nullable=True)
    oauth_token_secret = Column(String(255), nullable=True)

    basekit_packages = db.relationship("BaseKitPackage", backref="brand", lazy='dynamic')
    basekit_users = db.relationship("BaseKitUser", backref="brand", lazy='dynamic')
    basekit_sites = db.relationship("BaseKitSite", backref="brand", lazy='dynamic')

    def __repr__(self):
        return "<BaseKitBrand('%d', '%s')>" % (self.id, self.slug)

    @classmethod
    def _apply_active_filter(cls, query):
        return query.filter_by(provisioning_enabled=True)


class BaseKitPackage(BaseModel):

    """BaseKitPackage details."""
    __tablename__ = 'basekit_package'

    name = Column(String(64), nullable=True)
    description = Column(Text(64), nullable=True)
    cluster_id = Column(Integer, ForeignKey('basekit_cluster.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('basekit_brand.id'), nullable=False)
    bk_package_id = Column(String(64), unique=True, nullable=False)
    package_id = Column(Integer, ForeignKey('package.id'), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)

    package = db.relationship("Package")

    def __repr__(self):
        return "<BaseKitPackage('%d', '%s')>" % (self.id, self.name)


class BaseKitUser(BaseModel):
    """Records the state of basekit user instances that have been provisioned"""

    __tablename__ = 'basekit_user'

    brand_id = Column(Integer, ForeignKey('basekit_brand.id'), nullable=False)
    bk_user_id = Column(String(64), unique=True, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    bk_username = Column(String(64), unique=True, nullable=True)

    def __repr__(self):
        return "<BaseKitUser('%d')>" % (self.id)


class BaseKitSite(BaseModel):
    """Records the state of basekit site instances that have been provisioned"""
    __tablename__ = 'basekit_site'

    brand_id = Column(Integer, ForeignKey('basekit_brand.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    bk_site_id = Column(String(64), unique=True, nullable=True)
    basekit_package_id = Column(Integer, ForeignKey('basekit_package.id'), nullable=False)
    bk_template_ref = Column(String(64), unique=False, nullable=True)
    subdomain = Column(String(64), nullable=True, unique=True)
    status = Column(String(64), default='active', server_default='active', nullable=False)
    basekit_node_id = Column(Integer, ForeignKey('basekit_node.id'), nullable=True)

    basekit_domains = db.relationship("BaseKitDomain", backref="site", lazy='dynamic')
    basekit_package = db.relationship("BaseKitPackage", backref=db.backref("sites", lazy='dynamic'))
    basekit_node = db.relationship('BaseKitNode')
    # TODO the lack of direct link to customer is irritating.

    def __repr__(self):
        return "<BaseKitSite('%d')>" % (self.id)

    def to_json(self):
        obj = super(BaseKitSite, self).to_json()

        doms = self.basekit_domains.all()

        del obj['brand_id']
        del obj['bk_site_id']
        obj['package_id'] = obj['basekit_package_id']
        obj['template_id'] = obj['bk_template_ref']
        del obj['basekit_package_id']
        del obj['bk_template_ref']
        obj['service'] = 'builder'  # TODO: fix static hack

        # TODO implement real logic to determine primary domain
        # For now we just mark the subdomain as the primary domain
        obj['domains'] = [dom.to_json() for dom in doms]
        del obj['subdomain']

        node = BaseKitNode.query.get(obj['basekit_node_id'])
        obj['front_end_ip_addresses'] = [node.ip]
        if node.cname:
            obj['front_end_cnames'] = [node.cname]
        del obj['basekit_node_id']

        return obj

    @classmethod
    def get_for_customer_id(cls, customer_id):
        from test_models.core import User
        return cls.query_active_or_suspended.join(User).filter_by(customer_id=customer_id)


class BaseKitDomain(BaseModel):
    """Records the state of basekit domain instances that have been provisioned"""

    __tablename__ = 'basekit_domain'

    site_id = Column(Integer, ForeignKey('basekit_site.id'), nullable=False)
    bk_domain_id = Column(String(64), unique=True, nullable=True)
    domain = Column(String(255), unique=True, nullable=False)

    def __repr__(self):
        return "<BaseKitDomain('%d')>" % (self.id)

    def to_json(self):
        obj = super(BaseKitDomain, self).to_json()
        return {
            "domain": self.domain,
            "primary": self.domain == self.site.subdomain,
            "updated_at": obj['updated_at'],
            "created_at": obj['created_at'],
        }


class BaseKitPackageTemplate(BaseModel):
    """Contains a cache of basekit templates available for a given package"""

    __tablename__ = 'basekit_package_template'
    __table_args__ = (
        UniqueConstraint('package_id', 'template_ref'),
    )

    package_id = Column(Integer, ForeignKey('package.id'), nullable=False)
    template_ref = Column(String(64), unique=False, nullable=False)
    name = Column(String(120), unique=False, nullable=False)
    slug = Column(String(64), unique=False, nullable=False)  # Not presently unique; from 'directory' attr of /v2/templates

    package = db.relationship('Package', backref=db.backref('basekit_templates', lazy='dynamic'))

    def __repr__(self):
        return "<BaseKitPackageTemplate('%d')>" % (self.id)

    def to_json(self):
        return {
            "id": self.template_ref,
            "tag": self.slug,
            "name": self.name,
        }


class BaseKitProvisioningHelper:
    """ Helpers to do some of the dirty work of mapping Designs to BaseKit """

    @classmethod
    def map_partner_to_brand(cls, partner):
        """Find a brand object given a partner.  Assumes one active (prov enabled) partner cluster per partner"""
        return BaseKitBrand.query_active.filter(BaseKitBrand.partner == partner).filter(BaseKitCluster.provisioning_enabled == True).one()

    @classmethod
    def find_basekit_package(cls, brand, customer):
        from test_models.core import Package, CustomerPackage
        return brand.basekit_packages.join(Package).join(CustomerPackage).filter_by(customer=customer).first()

    @classmethod
    def find_unused_subdomain(cls, brand, desired_subdomain):
        domain = u'{}.{}'.format(desired_subdomain, brand.default_domain)
        if BaseKitSite.query.filter_by(subdomain=domain).count() == 0:
            return domain

        from . import db
        substring_matches = db.session.query(BaseKitSite.subdomain).filter(
            BaseKitSite.subdomain.like(u'{}%.{}'.format('test', brand.default_domain))).all()
        trimright = len(brand.default_domain) + 1

        def transform(x):
            try:
                return int(x)
            except Exception:
                return 0

        counter = 1
        candidates = [transform(sequence) for sequence in map(lambda x: x[0][len(desired_subdomain):-trimright], substring_matches)]
        if candidates:
            counter = max(candidates)

        valid = None
        while not valid:
            domain = u'{}{}.{}'.format(desired_subdomain, counter, brand.default_domain)
            valid = BaseKitSite.query.filter_by(subdomain=domain).count() == 0
            counter = counter + 1

        return domain
