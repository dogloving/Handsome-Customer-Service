from django.test import TestCase
from django.test.client import RequestFactory
from .apis import enterprise, helper, messages, customer
from . import models, const, const_table
import json, hashlib, time, random, string, datetime
import django.utils.timezone as timezone

def jrToJson(jr):
    '''将JsonResponse对象转为Json对象'''
    return json.loads(jr.content.decode('utf8'))

class CustomerLoginTestCase(TestCase):
    '''测试用户登录Api'''
    def setUp(self):
        md5 = hashlib.md5()
        salt = 'testsalt'
        password = 'password1'
        password += salt
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        models.Customer.objects.create(
            CID = 'test_cid', EID = 'test_eid', email = '2222@qq.com', salt = salt,
            password = password, icon = 'test_icon', name = 'test_name', state = 1,
            service_number = 0, serviced_number = 100, last_login = datetime.datetime.now()
        )

    def test_login(self):
        #测试登录成功
        info = {
            'email': '2222@qq.com',
            'password': 'password1'
        }
        rf = RequestFactory()
        request = rf.post('api/customer/login/')
        request._body = json.dumps(info).encode('utf8')
        request.session = {}
        self.assertEqual(jrToJson(customer.customer_login(request))['flag'],
        const_table.const.SUCCESS)
        #测试密码错误
        info['password'] = '123456789'
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_login(request))['flag'],
        const_table.const.WRONG_PASSWORD)
        #测试登录失败
        info['email'] = '123456@qq.com'
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_login(request))['flag'],
        const_table.const.WRONG_ACCOUNT)

class CustomerLogoutTestCase(TestCase):
    '''测试客服退出Api'''
    def setUp(self):
        models.Customer.objects.create(
            CID = 'test_cid1', EID = 'test_eid', email = '2222@qq.com', salt = 'salt',
            password = 'password', icon = 'test_icon', name = 'test_name', state = 2,
            service_number = 0, serviced_number = 100, last_login = datetime.datetime.now()
        )

    def test_logout(self):
        rf = RequestFactory()
        request = rf.post('api/customer/logout/')
        request.session = {}
        #登出失败
        info = {}
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_logout(request))['flag'],
        const_table.const.CID_NOT_EXIST)
        #登出成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_logout(request))['flag'],
        const_table.const.SUCCESS)

class OnlineStateTestCase(TestCase):
    '''测试改变在线状态'''
    def setUp(self):
        models.Customer.objects.create(
            CID = 'test_cid', EID = 'test_eid', email = '2222@qq.com', salt = 'salt',
            password = 'password', icon = 'test_icon', name = 'test_name', state = 2,
            service_number = 0, serviced_number = 100, last_login = datetime.datetime.now()
        )

    def test_online_state_change(self):
        rf = RequestFactory()
        request = rf.post('api/customer/change_ol/')
        request.session =  {}
        info = {}
        #失败
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_change_onlinestate(request))['flag'],
        const_table.const.CID_NOT_EXIST)
        #成功
        request.session['cid'] = 'test_cid'
        self.assertEqual(jrToJson(customer.customer_change_onlinestate(request))['flag'],
        const_table.const.SUCCESS)
        self.assertEqual(models.Customer.objects.get(CID = 'test_cid').state, 3)
        self.assertEqual(jrToJson(customer.customer_change_onlinestate(request))['flag'],
        const_table.const.SUCCESS)
        self.assertEqual(models.Customer.objects.get(CID = 'test_cid').state, 2)

class ServicedNumTestCase(TestCase):
    '''测试客服服务过的人数'''
    def setUp(self):
        models.Customer.objects.create(CID = 'test_cid', EID = 'test_eid', email = '2222@qq.com', salt = 'salt',
            password = 'password', icon = 'test_icon', name = 'test_name', state = 2,
            service_number = 0, serviced_number = 100, last_login = datetime.datetime.now())

    def test_serviced_number(self):
        CID = 'test_cid'
        result = customer.customer_serviced_number(CID)
        self.assertEqual(result, 100)

class CustomerOnedayTestCase(TestCase):
    '''测试客服24h的会话数'''
    def setUp(self):
        models.Dialog.objects.create(DID = '1', CID = 'test_cid1', 
                                    start_time = '2017-8-29 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '2', CID = 'test_cid1', 
                                    start_time = '2017-8-29 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '3', CID = 'test_cid1', 
                                    start_time = '2017-8-1 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '4', CID = 'test_cid2', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
    
    def test_customer_oneday(self):
        CID = 'test_cid1'
        result = customer.customer_dialogs_oneday(CID)
        self.assertEqual(result, 2)

class CustomerTotalMsgTestCase(TestCase):
    '''测试客服总消息数'''
    def setUp(self):
        models.Dialog.objects.create(DID = '1', CID = 'test_cid1', 
                                    start_time = '2017-8-29 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '2', CID = 'test_cid1', 
                                    start_time = '2017-8-29 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '3', CID = 'test_cid1', 
                                    start_time = '2017-8-1 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '4', CID = 'test_cid2', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Message.objects.create(MID = 'a', SID = 'wang', RID = 'zhang', DID = '1',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'b', SID = 'wang', RID = 'lee', DID = '1',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'c', SID = 'wang', RID = 'zhao', DID = '2',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'd', SID = 'wang', RID = 'zhang', DID = '2',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'e', SID = 'wang', RID = 'zhang', DID = '3',
                                    content = '123', date = '2017-8-1 17:00:00')
        models.Message.objects.create(MID = 'f', SID = 'wang', RID = 'zhang', DID = '3',
                                    content = '123', date = '2017-8-1 17:00:00')
        models.Message.objects.create(MID = 'g', SID = 'wang', RID = 'zhang', DID = '4',
                                    content = '123', date = '2017-8-9 17:00:00')

    def test_customer_total_msg(self):
        CID = 'test_cid1'
        result = customer.customer_total_messages(CID)
        self.assertEqual(result, 6)

class CustomerTotalServicedTimeTestCase(TestCase):
    '''测试客服服务的总分钟'''
    def setUp(self):
        models.Dialog.objects.create(DID = '1', CID = 'test_cid1', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '2', CID = 'test_cid1', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 17:30:05')
        models.Dialog.objects.create(DID = '3', CID = 'test_cid1', 
                                    start_time = '2017-8-9 17:05:32',
                                    end_time = '2017-8-9 17:27:01')
        models.Dialog.objects.create(DID = '4', CID = 'test_cid2', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-10 18:00:00')

    def test_customer_total_minute(self):
        CID = 'test_cid1'
        result = customer.customer_total_servicedtime(CID)
        self.assertAlmostEqual(result, 112, delta = 1)

class CustomerTotalDialogTestCase(TestCase):
    '''测试客服总会话数'''
    def setUp(self):
        models.Dialog.objects.create(DID = '1', CID = 'test_cid1', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '2', CID = 'test_cid1', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 17:30:05')
        models.Dialog.objects.create(DID = '3', CID = 'test_cid1', 
                                    start_time = '2017-8-9 17:05:32',
                                    end_time = '2017-8-9 17:27:01')
        models.Dialog.objects.create(DID = '4', CID = 'test_cid2', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')

    def test_total_dialog(self):
        CID = 'test_cid1'
        result = customer.customer_total_dialogs(CID)
        self.assertEqual(result, 3)

class CustomerAvgTimeTestCase(TestCase):
    '''测试客服会话平均时间'''
    def setUp(self):
        models.Dialog.objects.create(DID = '1', CID = 'test_cid1', UID = 7, 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '2', CID = 'test_cid1', UID = 7, 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 17:30:05')
        models.Dialog.objects.create(DID = '3', CID = 'test_cid1', UID = 77, 
                                    start_time = '2017-8-9 17:05:32',
                                    end_time = '2017-8-9 17:27:01')
        models.Dialog.objects.create(DID = '4', CID = 'test_cid2', UID = 7, 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')

    def test_customer_avg_time(self):
        CID = 'test_cid1'
        result = customer.customer_avgtime_dialogs(CID)
        self.assertAlmostEqual(result, 37, delta = 0.8)

class CustomerAvgMegTestCase(TestCase):
    '''测试客服平均消息数'''
    def setUp(self):
        models.Dialog.objects.create(DID = '1', CID = 'test_cid1', 
                                    start_time = '2017-8-29 17:00:00',
                                    end_time = '2017-8-29 19:00:00')
        models.Dialog.objects.create(DID = '2', CID = 'test_cid1', 
                                    start_time = '2017-8-29 17:00:00',
                                    end_time = '2017-8-29 18:00:00')
        models.Dialog.objects.create(DID = '3', CID = 'test_cid1', 
                                    start_time = '2017-8-2 18:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Dialog.objects.create(DID = '4', CID = 'test_cid2', 
                                    start_time = '2017-8-9 17:00:00',
                                    end_time = '2017-8-9 18:00:00')
        models.Message.objects.create(MID = 'a', SID = 'wang', RID = 'zhang', DID = '1',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'b', SID = 'wang', RID = 'lee', DID = '1',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'c', SID = 'wang', RID = 'zhao', DID = '2',
                                    content = '123', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'd', SID = 'wang', RID = 'zhang', DID = '2',
                                    content = '12358', date = '2017-8-29 17:00:00')
        models.Message.objects.create(MID = 'e', SID = 'wang', RID = 'zhang', DID = '3',
                                    content = '123', date = '2017-8-1 17:00:00')
        models.Message.objects.create(MID = 'f', SID = 'wang', RID = 'zhang', DID = '3',
                                    content = '123', date = '2017-8-1 17:00:00')
        models.Message.objects.create(MID = 'g', SID = 'wang', RID = 'zhang', DID = '4',
                                    content = '123', date = '2017-8-9 17:00:00')

    def test_avg_msg(self):
        CID = 'test_cid1'
        result = customer.customer_avgmes_dialogs(CID)
        self.assertAlmostEqual(result, 2, delta = 0.8)

class CustomerDialogListTestCase(TestCase):
    '''测试获取客服所有会话列表'''
    def setUp(self):
        CustomerAvgTimeTestCase.setUp(self)

    def test_customer_dialog_list(self):
        rf = RequestFactory()
        request = rf.post('api/customer/dialog_list/')
        request.session =  {}
        info = {}
        #成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_dialogs(request))['message']
        self.assertEqual(len(result), 3)
        self.assertEqual((result[1])['uid'], '7')
        #失败
        del request.session['cid']
        self.assertEqual(jrToJson(customer.customer_dialogs(request))['flag'],
        const_table.const.CID_NOT_EXIST)

class CustomerDialogMsgTestCase(TestCase):
    '''测试获取客服某个会话内容'''
    def setUp(self):
        CustomerAvgMegTestCase.setUp(self)

    def test_customer_dialog_msg(self):
        rf = RequestFactory()
        request = rf.post('api/customer/dialog_msg/')
        info = {
            'did': '2'
        }
        #成功
        request.session = {}
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_dialog_messages(request))['message']
        self.assertEqual(len(result), 2)
        self.assertEqual((result[1])['content'], '12358')

class CustomerModifyTestCase(TestCase):
    '''测试客服修改'''
    def setUp(self):
        CustomerLogoutTestCase.setUp(self)

    def test_customer_modify(self):
        rf = RequestFactory()
        request = rf.post('api/customer/modify/')
        request.session =  {}
        info = {
            'icon': 'umaru',
            'name': 'Takahashi'
        }
        #成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_modify_icon(request))['flag'],
        const_table.const.SUCCESS)
        self.assertEqual(models.Customer.objects.get(CID = 'test_cid1').name, 'Takahashi')
        self.assertEqual(models.Customer.objects.get(CID = 'test_cid1').icon, 'umaru')
        #失败
        del request.session['cid']
        self.assertEqual(jrToJson(customer.customer_modify_icon(request))['flag'],
        const_table.const.CID_NOT_EXIST)

class allDataTestCase(TestCase):
    '''测试返回客服所有数据'''
    def setUp(self):
        CustomerAvgMegTestCase.setUp(self)
        CustomerLogoutTestCase.setUp(self)

    def test_all_data(self):
        rf = RequestFactory()
        request = rf.post('api/customer/get_alldata/')
        request.session =  {}
        info = {}
        #成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        self.assertEqual(jrToJson(customer.customer_get_alldata(request))['flag'],
        const_table.const.SUCCESS)
        #失败
        del request.session['cid']
        self.assertEqual(jrToJson(customer.customer_get_alldata(request))['flag'],
        const_table.const.CID_NOT_EXIST)

class CustomerGetInfoTestCase(TestCase):
    '''测试客服获取个人信息'''
    def setUp(self):
        CustomerLogoutTestCase.setUp(self)
        models.Enterprise.objects.create(EID = 'test_eid')

    def test_get_info(self):
        rf = RequestFactory()
        request = rf.post('api/customer/get_info/')
        request.session =  {}
        info = {}
        #成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_get_info(request))['message']
        self.assertEqual(result['eid'], 'test_eid')
        self.assertEqual(result['name'], 'test_name')
        #失败
        del request.session['cid']
        self.assertEqual(jrToJson(customer.customer_get_info(request))['flag'],
        const_table.const.CID_NOT_EXIST)

class CustomerGetIDTestCase(TestCase):
    '''测试客服获取id'''
    def setUp(self):
        CustomerLogoutTestCase.setUp(self)
        models.Enterprise.objects.create(EID = 'test_eid')

    def test_get_id(self):
        rf = RequestFactory()
        request = rf.post('api/customer/get_id/')
        request.session =  {}
        info = {}
        #成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_get_info(request))['message']
        self.assertEqual(result['eid'], 'test_eid')
        self.assertEqual(result['cid'], 'test_cid1')
        #失败
        del request.session['cid']
        self.assertEqual(jrToJson(customer.customer_get_info(request))['flag'],
        const_table.const.CID_NOT_EXIST)

class CustomerOtherOnlineTestCase(TestCase):
    '''测试获取其他在线客服'''
    def setUp(self):
        models.Customer.objects.create(
            CID = 'test_cid1', EID = 'test_eid1', state = 3, last_login = datetime.datetime.now()
        )
        models.Customer.objects.create(
            CID = 'test_cid2', EID = 'test_eid1', state = 2, last_login = datetime.datetime.now()
        )
        models.Customer.objects.create(
            CID = 'test_cid3', EID = 'test_eid1', state = 3, last_login = datetime.datetime.now()
        )
        models.Customer.objects.create(
            CID = 'test_cid4', EID = 'test_eid2', state = 2, last_login = datetime.datetime.now()
        )

    def test_customer_other_online(self):
        rf = RequestFactory()
        request = rf.post('api/customer/get_other_online/')
        request.session =  {}
        info = {}
        #成功
        request.session['cid'] = 'test_cid1'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_other_online(request))['message']
        self.assertEqual(len(result), 1)
        #失败
        del request.session['cid']
        self.assertEqual(jrToJson(customer.customer_other_online(request))['flag'],
        const_table.const.CID_NOT_EXIST)

class CustomerModifyPwdTestCase(TestCase):
    '''测试客服改密码'''
    def setUp(self):
        CustomerLoginTestCase.setUp(self)

    def test_modify_password(self):
        rf = RequestFactory()
        request = rf.post('api/customer/modify_password/')
        request.session =  {}
        info = {
            'old': 'password1',
            'new': 'sometimes_stupid'
        }
        #成功
        request.session['cid'] = 'test_cid'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_modify_password(request))['flag']
        self.assertEqual(result, const_table.const.SUCCESS)
        new_pwd = info['new']
        new_salt = models.Customer.objects.get(CID = 'test_cid').salt
        md5 = hashlib.md5()
        md5.update((new_pwd + new_salt).encode('utf8'))
        self.assertEqual(md5.hexdigest(), models.Customer.objects.get(CID = 'test_cid').password)

    def test_modify_fail(self):
        rf = RequestFactory()
        request = rf.post('api/customer/modify_password/')
        request.session =  {}
        info = {
            'old': 'always_handsome',
            'new': 'sometimes_stupid'
        }
        #旧密码不对
        request.session['cid'] = 'test_cid'
        request._body = json.dumps(info).encode('utf8')
        result = jrToJson(customer.customer_modify_password(request))['flag']
        self.assertEqual(result, const_table.const.WRONG_PASSWORD)
