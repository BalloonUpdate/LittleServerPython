import ctypes
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

import yaml

from dir_hash import dir_hash
from file import File

version_text = '1.0'

if __name__ == '__main__':
    try:
        print('updater单文件服务端(不建议用在正式环境)')

        try:
            ctypes.windll.kernel32.SetConsoleTitleW("LittleServer "+version_text)
        except:
            pass

        cfg = File('config.yml')

        cfgcontent = 'address: 0.0.0.0\nport: 8888'

        if cfg.exists:
            print("读取配置文件config.yml")
            cfgcontent = cfg.content

        print('----------')
        print(cfgcontent)
        print('----------')

        obj = yaml.load(cfgcontent, yaml.SafeLoader)

        address = obj['address']
        port = obj['port']

        # 生成校验文件
        print(f'正在启动')
        for d in File('.'):
            if d.isDirectory:
                content = json.dumps(dir_hash(d), ensure_ascii=False, indent=4)
                d.parent(d.name + '.json').content = content

        print('http server 正在运行...')
        print('访问地址: http://'+('127.0.0.1' if address == '0.0.0.0' else address)+':'+str(port))

        server = HTTPServer((address, port), SimpleHTTPRequestHandler)
        server.serve_forever()
    except BaseException as e:
        raise e
        input("发生错误，按任意键退出..")
