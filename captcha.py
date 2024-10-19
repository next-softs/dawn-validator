import config
from twocaptcha import TwoCaptcha


solver = TwoCaptcha(config.token_captcha)

async def image_to_txt(img64):
    return solver.normal(img64, case=True, comment="Введите текст с картинки, регистр ВАЖЕН!")

async def report_answer(captchaId):
    return solver.report(captchaId, False)
