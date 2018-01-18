import sys
import time
from configparser import ConfigParser

from watchdog.events import *
from watchdog.observers import Observer

import charset
import subprocess

# 配置文件名称
INI_FILE = 'my.ini'
# maven安装路径
maven_path = None
# 包扫描目录
scan_dir = None


# 创建配置文件
if not os.path.exists(INI_FILE):
    with open(INI_FILE, 'w', encoding='utf-8') as f:
        f.write('[config]\n')
        f.write('# maven安装路径(例如：D:/maven)\n')
        f.write('maven_path=\n')
        f.write('# jar包扫描目录(例如：D:/myLib/jars)\n')
        f.write('scan_dir=')
    print('请在my.ini文件中配置maven安装路径和jar包扫描目录，然后重新运行该程序')
    input('按enter键退出...')
    sys.exit()

# 读取配置文件
config = ConfigParser()
config.read(INI_FILE, charset.detect(INI_FILE))
maven_path = config.get("config", "maven_path", fallback=None)
scan_dir = config.get("config", "scan_dir", fallback=None)

# 检测路径
if maven_path and os.path.exists(maven_path):
    if (not maven_path.endswith('/')) or (not maven_path.endswith('\\')):
        maven_path += '/'
    maven_path += 'bin/'
else:
    print('请确认' + INI_FILE + '文件中maven安装路径:"maven_path"是否正确配置')

if not scan_dir or not os.path.exists(scan_dir):
    print('请确认' + INI_FILE + '文件中jar包扫描目录:"scan_dir"是否正确配置')


# 监控目录变化处理类
class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    # def on_moved(self, event):
    #     if event.is_directory:
    #         print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
    #     else:
    #         print("file moved from {0} to {1}".format(event.src_path, event.dest_path))
    #
    # def on_created(self, event):
    #     if event.is_directory:
    #         print("directory created:{0}".format(event.src_path))
    #     else:
    #         print("file created:{0}".format(event.src_path))
    #
    # def on_deleted(self, event):
    #     if event.is_directory:
    #         print("directory deleted:{0}".format(event.src_path))
    #     else:
    #         print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        print(time.strftime('%Y-%m-%d %H:%M:%S'))
        if event.is_directory:
            print("修改的目录:{0}".format(event.src_path))
        else:
            file_path = event.src_path
            print("修改的文件:{0}".format(file_path))
            basename = os.path.basename(file_path)
            file_info = os.path.splitext(basename)
            file_name = file_info[0]  # 文件名
            suffix = file_info[1]  # 文件后缀
            # 校验文件格式
            if suffix != '.jar':
                return
            # 校验文件名称格式
            jar_info = file_name.split('-')
            if len(jar_info) != 3:
                print('文件请按照：groupId-artifactId-version.jar 的格式命名，示例：com.oracle-ojdbc14-10.2.1.jar')
                return

            cmd = '{0}mvn install:install-file -Dfile={1} -DgroupId={2} -DartifactId={3} -Dversion={4} -Dpackaging=jar'\
                .format(maven_path, file_path, jar_info[0], jar_info[1], jar_info[2])
            # 执行maven安装jar包命令
            # os.system(command=cmd)
            subprocess.Popen(cmd, shell=True)


if __name__ == "__main__":
    try:
        observer = Observer()
        event_handler = FileEventHandler()
        observer.schedule(event_handler, scan_dir, True)
        observer.start()
        print(scan_dir + ' 目录监控中...')
    except Exception as e:
        print('程序运行异常，异常详情：', e)
        input('按enter键退出...')
        sys.exit()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
