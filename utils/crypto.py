import base64
import hashlib


def md5(text):
    # md5加密
    m = hashlib.md5()
    mdr_str = text.encode()
    m.update(mdr_str)
    ciphertext = m.hexdigest()
    return ciphertext


def base64encrypt(content):
    # base64加密
    b_content = content.encode("utf-8")
    b_base64_content = base64.encodebytes(b_content)
    base64_content = b_base64_content.decode("utf-8")
    return base64_content


def base64decrypt(content):
    # base64解密
    b_base64_content = content.encode("utf-8")
    b_content = base64.decodebytes(b_base64_content)
    origin_text = b_content.decode("utf-8")
    return origin_text


if __name__ == '__main__':
    t = md5('http://china.findlaw.cn/ask/question_20146066.html')
    print(t)
