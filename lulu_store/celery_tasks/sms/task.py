from celery_tasks.main import app

# 验证码短信模板
from lulu_store.libs.yuntongxun.sms import CCP

# 短信验证码模板！
SMS_CODE_TEMP_ID = 1


@app.task(name='send_sms_code')
def send_sms_code(mobile, code, expires):
    """
    发送短信验证码
    :param mobile: 手机号
    :param code: 验证码
    :param expires: 有效期ß
    :return: None
    """
    ccp = CCP()
    result = ccp.send_template_sms(mobile, [code, expires], SMS_CODE_TEMP_ID)
