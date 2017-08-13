from backend import models
import time, hashlib, datetime, random, string, math

eid = '61078407c29755d8c080cb31ec09795d'
cids = ['test_cid5', 'test_cid6', 'test_cid7', 'test_cid8', 'test_cid9',
        'test_cid10', 'test_cid11', 'test_cid12', 'test_cid13', 'test_cid14', 'test_cid15']
uids = ['test_uid3', 'test_uid4', 'test_uid5', 'test_uid6', 'test_uid7', 'test_uid8', 'test_uid9',
        'test_uid10', 'test_uid11', 'test_uid12', 'test_uid13', 'test_uid14', 'test_uid15']
messages = ['你好', '毕竟too young', 'naive', 'excited', '谈笑风生', '比你们不知道高到哪里去了',
        '长者的身份', '董先生连任好不好啊', '吼啊', '打工是不可能打工的', '这辈子都不可能打工的',
        '超喜欢这里的', '说话又好听', '做生意嘛又不会', '人生经验']
questions = [
    {'question': '怎么看待励志书籍？', 'answer': '看再多，那都是别人的人生'},
    {'question': '＂知行合一＂到底如何理解？', 'answer': '  知道做不到，等于不知道。'},
    {'question': '如何反驳＂现实点，这个社会就是这样＂？', 'answer': ' 你是怎样，你的世界就是怎样。'},
    {'question': '有哪些道理是你读了不信，听不进去，直到你亲身经历方笃信不疑的？', 'answer': '不要低估你的能力，不要高估你的毅力。'},
    {'question': '做哪些事情可以提升生活品质？', 'answer': '定期扔东西。'},
    {'question': '什么叫见过大世面？', 'answer': '能享受最好的，也能承受最坏的。'},
    {'question': '你对自由的理解是什么？', 'answer': ' 说＂不＂的能力。'},
    {'question': '你是如何走出人生的阴霾的？', 'answer': ' 多走几步。'},
    {'question': '1+1=？', 'answer': '2'},
    {'question': '美国首都？', 'answer': '华盛顿'},
    {'question': '天王盖地虎？', 'answer': '宝塔镇河妖'},
    {'question': '草色烟光残照里?', 'answer': '无言谁会凭栏意'},
    {'question': '几度饮散歌阑？', 'answer': '香暖鸳鸯被'}
]
categories = ['人生', '常见', '技术', '产品', '售后', '运维']
names = ['库', '里', '汤', '普', '森', '杜', '兰', '特', '格', '林', '科', '尔', '尼', '克', '杨', '麦', '基']
def generate_name():
    """随机生成名字"""
    return random.choice(names) + random.choice(names)

def generate_str():
    """随机生成字符串"""
    time.sleep(0.01)
    md5 = hashlib.md5()
    md5.update((str(int(time.time())) + (random.choice(names)
     + random.choice(names) + random.choice(names) + random.choice(names))).encode('utf8'))
    return md5.hexdigest()

def generate_email():
    """随机生成email"""
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    return salt + '@hs.com'

def delta(num):
    """生成时间差"""
    return datetime.timedelta(minutes = num)

def generate_messages(uid, cid):
    """给两个人随机生成一段对话，并且生成一个dialog"""
    did = generate_str()
    time1 = datetime.datetime.now()
    models.Dialog.objects.create(DID = did, EID = eid, start_time = time1 - delta(-4), end_time = time1,
        UID = uid, CID = cid, feedback = random.choice([1, 2, 3, 4, 5]))
    message_length = random.choice([i for i in range(15)])
    for i in range(message_length):
        mid = generate_str()
        content = random.choice(messages)
        sid = random.choice([uid, cid])
        rid = uid if sid == uid else cid
        date = time1
        models.Message.objects.create(MID = mid, SID = sid, RID = rid, content = content, DID = did, date = date)

def generate_question():
    """给企业随机生成一些问题"""
    for item in questions:
        question = item['question']
        answer = item['answer']
        qid = generate_str()
        category = random.choice(categories)
        models.Question.objects.create(QID = qid, question = question, answer = answer, category = category, EID = eid)

def generate_customer():
    """给企业添加客服"""
    for cid in cids:
        email = generate_email()
        name = generate_name()
        icon = '/static/img/customer_icon/uh_' + str(random.choice([i + 1 for i in range(9)])) + '.gif'
        state = random.choice([i - 1 for i in range(4)])
        serviced_number = random.choice([i for i in range(100)])
        service_number = random.choice([i for i in range(100)])
        raw_password = 'password'
        salt = 'salt'
        md5 = hashlib.md5()
        md5.update((raw_password + salt).encode('utf8'))
        models.Customer.objects.create(CID = cid, EID = eid, email = email, name = name, icon = icon,
            state = state, serviced_number = serviced_number, service_number = service_number,
            salt = salt, password = md5.hexdigest(), last_login = datetime.datetime.now()
            )

def generate_dialog():
    """随机生成会话"""
    for i in range(20):
        uid = random.choice(uids)
        cid = random.choice(cids)
        generate_messages(uid, cid)

#客服
generate_customer()
#问题
generate_question()
#会话
generate_dialog()