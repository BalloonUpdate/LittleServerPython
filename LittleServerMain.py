import ctypes
import json
import sys
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
import yaml
from file import File


def getMetadata():
    temp = File(getattr(sys, '_MEIPASS', ''))
    return json.loads(temp('meta.json').content)


version = getMetadata()['version']
commit = getMetadata()['commit']
compile_time = getMetadata()['compile_time']
inDev = not getattr(sys, 'frozen', False)


class UpdaterHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/index.yml':
            self.respondWithContent(yaml.safe_dump({
                'version': "3.0",
                'server_type': "little",
                'update': 'res',
                **indexYaml
            }, sort_keys=False))
        elif self.path == '/' + resDir.name + '.yml':
            self.respondWithContent(yaml.safe_dump(self.hashDir(resDir), sort_keys=False))
        else:
            super(UpdaterHttpRequestHandler, self).do_GET()

    def respondWithContent(self, data: str):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/plain')
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Last-Modified", self.date_time_string())
        self.end_headers()

        self.wfile.write(data.encode('utf-8'))

    def hashDir(self, directory: File):
        structure = []
        for f in directory:
            if f.isFile:
                structure.append({'name': f.name, 'length': f.length, 'hash': f.sha1})
            if f.isDirectory:
                structure.append({'name': f.name, 'children': self.hashDir(f)})
        return structure


def check():
    if not workDir.exists:
        print('找不到工作目录' + workDir.path)
        sys.exit(1)

    if not configFile.exists:
        print('找不到配置文件' + configFile.name)
        sys.exit(1)

    if not resDir.exists:
        print('找不到资源目录' + resDir.path)
        sys.exit(1)


if __name__ == '__main__':
    try:
        print('正在启动文件更新助手服务端单文件版v'+version+' (开源地址: https://github.com/updater-for-minecraft)')

        try:
            ctypes.windll.kernel32.SetConsoleTitleW("文件更新助手服务端 "+version)
        except:
            pass

        workDir = File('.')
        resDir = workDir('res')
        configFile = workDir('config.yml')

        check()

        configObject = yaml.load(configFile.content, yaml.SafeLoader)
        address = configObject['address']
        port = configObject['port']

        indexYaml = {'mode': configObject['mode'], 'paths': configObject['paths']}

        print('文件更新助手服务端已经启动!')
        print('API地址: http://'+('127.0.0.1' if address == '0.0.0.0' else address)+':'+str(port)+'/index.yml')

        server = HTTPServer((address, port), UpdaterHttpRequestHandler)
        server.serve_forever()
    except BaseException as e:
        raise e
