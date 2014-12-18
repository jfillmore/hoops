import simplejson as json
from hoops import create_api

from tests import TestBase, app_config, db_config, log_config
from test_models.core import Partner, Language, PartnerAPIKey, Service, Package, PackageService, PackageServiceParam, Customer, CustomerPackage, User
from test_models.basekit import BaseKitBrand, BaseKitCluster, BaseKitNode, BaseKitPackage, BaseKitPackageTemplate, BaseKitUser, BaseKitSite


api = None


class APITestBase(TestBase):

    @classmethod
    def get_app(cls):

        app, db = create_api(app_config=app_config,
                             db_config=db_config,
                             log_config=log_config,
                             app_name='hoops',
                             flask_conf={'DEBUG': True,
                                         'ENVIRONMENT_NAME': 'test'})
        cls.db = db
        return app

    @classmethod
    def setup_app(cls):
        app = cls._app
        with app.app_context():
            cls.bypass_oauth()

    @classmethod
    def bypass_oauth(cls):
        app = cls._app
        l = Language(lang='en', name="English")
        p = Partner(name='test partner', language=l, output_format='json')
        ak = p.generate_api_key('testing')
        cls.db.session.add_all([l, p, ak])
        cls.db.session.commit()
        cls.db.session.refresh(ak)
        cls.db.session.refresh(ak.partner)
        app.config['TESTING_PARTNER_API_KEY'] = ak

    def populate_default_partner(cls):
        p = Partner.query.filter_by(name='test partner').first()
        en = Language.query.filter_by(lang='en').first()
        if not en:
            en = Language(lang='en', name='English', active=1)
            cls.db.session.add(en)
        test_pkg1 = Package(name='test page site', description='Basic page site')
        p.packages.append(test_pkg1)
        c3 = Customer(partner=p, name='test customer')
        p.customers.append(c3)
        c3.packages.append(CustomerPackage(package=test_pkg1))
        u3 = User(partner=c3.partner, firstname='Test', lastname='User III', language=en, my_identifier='test_user_3', email='test_3@example.in',
                  customer=c3)
        builder = Service.query.filter_by(name='builder').first()
        if not builder:
            builder = Service(name='builder')
        ps = cls._add_package_service(test_pkg1, builder)
        cls.db.session.add_all([p, test_pkg1, c3, u3, builder, ps])
        cls.db.session.commit()

    @classmethod
    def populate(cls, use_db=None):
        if use_db:
            db = use_db
        en = Language.query.filter_by(lang='en').first()
        if not en:
            en = Language(lang='en', name='English', active=1)
            db.session.add(en)

        dev = Partner(name='dev', language=en, output_format='json')
        dev_key = PartnerAPIKey(**{
            'consumer_key': u'dev',
            'consumer_secret': u'XVgpEgeYld3lhjTu9ZXoxVkjku2TQFlfUbuxA4paU18',
            'enabled': True,
            'partner': dev,
            'token': u'hiMu97KpzlN2ttay3JI3Yhzq7aeYrILP3PLX7Pfg8jU',
            'token_secret': u'gSaX071iHzijyqiVpKecgUxVyUgMBDH4TQYCeQLQTQE',
        })
        enom = Partner(name='enom', language=en, output_format='json')
        enom_key = enom.generate_api_key('enom')
        builder = Service.query.filter_by(name='builder').first()
        if not builder:
            builder = Service(name='builder')
        dev_pkg1 = Package(name='Resellers Basic Account', description='Resellers Basic Account - from bkreseller.com')
        dev_pkg2 = Package(name='5 page site', description='Basic 5 page site')
        dev.packages.append(dev_pkg1)
        dev.packages.append(dev_pkg2)
        enom_pkg1 = Package(name='1 page site', description='Basic 1 page site')
        enom_pkg2 = Package(name='5 page site', description='Basic 5 page site')
        enom.packages.append(enom_pkg1)
        enom.packages.append(enom_pkg2)

        for package in [dev_pkg1, dev_pkg2, enom_pkg1, enom_pkg2]:
            cls._add_package_service(package, builder)

        c1 = Customer(partner=dev, name='dev-customer-1')
        c2 = Customer(partner=enom, name='enom-customer-1')
        dev.customers.append(c1)
        enom.customers.append(c2)
        c1.packages.append(CustomerPackage(package=dev_pkg1))
        c2.packages.append(CustomerPackage(package=enom_pkg2))
        enom.customers.append(Customer())
        enom.customers.append(Customer())
        u = User(partner=c1.partner, firstname='Roy', lastname='Hooper', language=en, my_identifier='test_user', email='test@example.in', customer=c1)
        u2 = User(partner=c2.partner, firstname='Test', lastname='User', language=en, my_identifier='test_user_2', email='test_1@example.in',
                  customer=c2)

        db.session.add_all([
            en, dev, enom, dev_key, enom_key, builder, dev_pkg1, dev_pkg2, enom_pkg1, enom_pkg2,
            c1, c2, u, u2
        ])

        db.session.commit()

        cluster = BaseKitCluster(name='BK Stage', description='BaseKit Staging Environment', api_url='http://rest.bkreseller.com')
        db.session.add(cluster)
        cluster.basekit_nodes.append(BaseKitNode(ip='50.18.217.93', cname='foo.example.com', instance_count=0, max_instances=0))
        brand = BaseKitBrand(name='enom-test', partner=enom, default_domain='bkreseller.com', oauth_consumer_key='enom',
                             oauth_consumer_secret='11809547934a6ab63ee3736188546c1c5f7aebd5', oauth_token='3fa1cb3399ca7f20e0ae3649beae1472b70748bc',
                             oauth_token_secret='6053eb08944b1c8f4faf9e977bff1ea8fc05e997', bk_brand_id=24)
        #brand2 = BaseKitBrand(name='enom-test', partner=dev, default_domain='bkreseller.com', oauth_consumer_key='enom',
        #                      oauth_consumer_secret='11809547934a6ab63ee3736188546c1c5f7aebd5',
        #                      oauth_token='3fa1cb3399ca7f20e0ae3649beae1472b70748bc',
        #                      oauth_token_secret='6053eb08944b1c8f4faf9e977bff1ea8fc05e997', bk_brand_id=24)
        cluster.basekit_brands.append(brand)
        #cluster.basekit_brands.append(brand2)
        db.session.commit()

        db.session.refresh(cluster)
        #bk = BaseKitAPIClient('brands/24/packages').get(dict(productType='subscription',active=1))
        bkp = BaseKitPackage(name='Resellers Basic Account', cluster=cluster, bk_package_id=810, package=brand.partner.packages[1])
        brand.basekit_packages.append(bkp)
        db.session.add(BaseKitUser(brand=brand, bk_user_id='fake', user=u))
        db.session.add(BaseKitSite(brand=brand, user=u, bk_site_id='fake', basekit_package=bkp, subdomain='faketest.bkreseller.com',
                       basekit_node_id=cluster.basekit_nodes[0].id))
        db.session.commit()

        pkgs = Package.query.all()
        tpls = [
            {
                u'directory': u'yelaudio',
                u'name': u'YelAudio',
                u'ref': 1,
            },
            {
                u'directory': u'wolfhorizon',
                u'name': u'Wolf Horizon',
                u'ref': 2,
            }]
        for pkg in pkgs:
            pkg.basekit_templates = [BaseKitPackageTemplate(name=tpl['name'], slug=tpl['directory'], template_ref=tpl['ref'])
                                     for tpl in tpls]

        db.session.commit()

    @classmethod
    def _add_package_service(cls, package, builder):
        ps = PackageService(service=builder)
        package.package_services.append(ps)
        pages = 1 if "1 page" in package.name else 5
        ps.params.append(PackageServiceParam(param_name='page_limit', param_value=pages))
        return ps

    def validate(self, rv, message):

        try:
            data = json.loads(rv.data)
        except json.decoder.JSONDecodeError as e:
            assert False, 'Failed to decode JSON: %s -- %s' % (e, rv.data)

        assert data['status_code'] == message.status_code, \
            "Got %s expected %s: %s" % (data['status_code'], message.status_code, rv.data)

        assert rv.status_code == int(message.http_status), rv.status_code

        try:
            check_for_parameter_leaks(data)
        except BaseKitLeak as e:
            assert False, "Found basekit reference in output: %s - %s" % (e, rv.data)

        ## Return the JSONdata for further testing.
        return data


class BaseKitLeak(Exception):
    pass


class PartnerIDLeak(Exception):
    pass


def check_for_parameter_leaks(data):
    try:
        recursive_check_for_parameter_leaks(data)
    except (PartnerIDLeak, BaseKitLeak) as e:
        assert False, '%s %s' % (e, data)


def recursive_check_for_parameter_leaks(data):
    if type(data) == dict:
        for key in data.keys():
            if key == 'basekit':
                raise BaseKitLeak("key 'basekit' found")
            if key == 'partner_id':
                raise PartnerIDLeak("key 'partner_id' found")
            recursive_check_for_parameter_leaks(data[key])
    if type(data) == list:
        for item in data:
            recursive_check_for_parameter_leaks(item)
    if data == 'basekit':
        raise BaseKitLeak("value 'basekit' found")
    if data == 'partner_id':
        raise PartnerIDLeak("value 'partner_id' found in")
