from os.path import isfile,splitext,isdir,basename,dirname,exists,join,normpath,relpath,realpath
from os.path import split as split_path
from os import unlink,getcwd,rename,walk,system,listdir,makedirs,get_terminal_size
from zipfile import ZipFile
from tkinter.filedialog import askdirectory
from abc import abstractmethod
from copy import deepcopy
from typing import Literal,Any
from wcwidth import wcswidth
from py7zr import SevenZipFile
from json import load,dumps

import re
import shutil
import requests

from GT_Config import DEFAULT_CONFIG,DEFAULT_CHINESE_CONFIG

#DEFINE
proxy:int = None #代理端口

header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}

client_url = "http://downloads.gtnewhorizons.com/ClientPacks/?raw"
server_url = "http://downloads.gtnewhorizons.com/ServerPacks/?raw"

OLD_VERSION_PATH = None
NEED_MOVE_FILE = True
NOW_VERSION = None

class FileType:
    '''处理文件描述'''
    LOCAL = "local"
    ONLINE = "online"
    
    NR_MV = "nr_mv"
    MV = "mv"
    CP = "cp"
    RM = "rm"
    UNZIP = "unzip"
    
    ATTR_ENABLED = "enabled"
    ATTR_DESC = "description"

    ATTR_FP = "file_path"    
    ATTR_FN = "file_name"
    
    ATTR_WP = "work_path"
    ATTR_SP = "save_path"
    ATTR_TYPE = "type"
    ATTR_URL = "url"
    ATTR_REZIP = "retain_zip"
    ATTR_ACTION = "action_type"
    ATTR_SCRIPT = "script"
    ATTR_VERSION_DEMAND = "version_demand"
    ATTR_CONFIG_OPTION = "config_option"
    ATTR_DEFAULT_CONFIG = "default_config"
    ATTR_SERVER_DETAIL = "server_detail"
    
    def __init__(self, kwargs:dict[str,Any]) -> None:
        self.enabled:bool = False
        self.file_path:str = None
        self.file_name:str = None
        self.save_path:tuple = None
        self.work_path:tuple = None
        self.type:str = None
        self.description:str = None
        self.url:str = None
        self.retain_zip:bool = True
        self.action_type:Literal["mv","nr_mv","cp","rm","unzip"] = None
        self.script:list = None
        self.version_demand:str | list = None
        self.config_option:list = []
        self.default_config:str = None
        self.server_detail:bool = False
        for key,value in kwargs.items():
            self.__setattr__(key,value)
        self.init_path("file_path")
        self.init_path("work_path")
        self.init_path("save_path")
        if self.file_path == None:
            self.file_path = self.join_path(self.save_path,self.file_name)
        
    def init_path(self,attr:str):
        """将路径参数初始化"""
        raw_path = self.__getattribute__(attr)
        if isinstance(raw_path,str):
            self.__setattr__(attr,normpath(raw_path))
        elif isinstance(raw_path,tuple):
            self.__setattr__(attr,normpath(join(*raw_path)))
    
    def join_path(self,main_path,args:str | tuple):
        if isinstance(args,tuple):
            return join(main_path,*args)
        elif isinstance(args,str):
            return join(main_path,args)

    def _action_local(self):
        match self.action_type:
            #rm file
            case FileType.RM:
                pb = progress_bar(title = f"删除 {self.file_path} {self.description}")
                if self.save_path:
                    work = FileManage(work_path = self.save_path)
                    files = work.lsdir()
                    for path in files:
                        if re.findall(self.file_name,FileManage(file_path = path).file_name):
                            work.rm(path)
                            break
                else:
                    FileManage.rm(self.file_path)
                pb.finish()
            
            #cp file
            case FileType.CP:
                global OLD_VERSION_PATH,NEED_MOVE_FILE
                if not NEED_MOVE_FILE:
                    return
                if not OLD_VERSION_PATH:
                    print("请选择需要转移的文件的游戏根目录")
                    OLD_VERSION_PATH = realpath(askdirectory(title="请选择需要转移的文件的游戏根目录"))
                    if not OLD_VERSION_PATH:
                        NEED_MOVE_FILE = False
                        return
                        
                old_filepath = join(OLD_VERSION_PATH,self.file_path)
                if exists(old_filepath):
                    pb = progress_bar(title=f"移动 {self.file_path} -> {self.save_path}")
                    FileManage.cp(old_filepath,self.save_path)
                    pb.finish()
            
            #unzip
            case FileType.UNZIP:
                FileManage(self.save_path).unzip(self.file_path,retain = self.retain_zip)
            
        #edit file
        for sec,opt,value in self.config_option:
            if self.check_version():
                pd = progress_bar(title=f"设置 {opt} => {value} {self.description}")
                FileManage.touch(self.file_path,self.default_config)
                fileconfig = Config(self.file_path).Config
                fileconfig.set_config(sec,opt,value)
                fileconfig.save()
                pd.finish()
        
        self._action_script()
        
    def _action_online(self):
        if self.check_version() and self.url:
            file_path = url_manage.dowload(self.url,self.save_path,self.file_name)
            if self.action_type == FileType.UNZIP:
                FileManage(self.save_path).unzip(file_path,retain = self.retain_zip)
        self._action_script()
    
    def _action_script(self):
        if self.script:
            for script in self.script:
                script = FileType(script)
                script.action()
           
    def check_version(self) ->bool:
        '''版本要求'''
        demand = self.version_demand            
        if demand == None:
            return True
        now_version = GTNH.version()
        if isinstance(demand,list):
            if now_version in demand:
                return True
        elif isinstance(demand,str):
            chain:str = demand[0]
            version = demand[1:]
            match chain:
                case ">":
                    if now_version >= version:  return True
                case "<":
                    if now_version <= version:  return True
                case "=":
                    if now_version == version:  return True
                case _ as x:
                    if x.lower() == "all":
                        return True
                    raise ValueError(f"配置错误 {demand}")
        return False
        
    def action(self):
        if not self.enabled and self.check_version():
            return
        match self.type:
            case FileType.LOCAL:
                self._action_local()
            case FileType.ONLINE:
                self._action_online()
            case _:
                ValueError("配置文件类型错误")

class entry:
    '''设置项的描述'''
    def __init__(self,conf,value,index:int,chain:str,prefix:str,other:str) -> None:
        self.conf = conf
        self.value = value
        self.index = index
        self.chain = chain
        self.prefix = prefix
        self.other = other
        self.format = "{prefix}{conf}{chain}{value}{other}"
    
    def __str__(self) -> str:
        return self.format.format(conf = self.conf, chain = self.chain, value = self.value, prefix = self.prefix, other = self.other)

class ini_config:
    '''ini文件实现\n
    继承后必须实现的方法：ini_config_rule'''
    def __init__(self,path) -> None:
        self.path = path
        self._configs:dict[str,dict[str,entry]] = {}
        self._index_to_location:dict[int,dict[str,str]] = {}
        self.init_configs()
        self._change_index = set()
    
    def configs(self) -> dict[str,dict[str,str]]:
        configs = deepcopy(self._configs)
        for sec in configs.keys():
            for opt in configs[sec].keys():
                configs[sec][opt] = configs[sec][opt].value
        
        return configs
        
    @abstractmethod
    def init_config_rule(self):
        """
        必须初始化三个属性参数\n
        attr【_section_rule， _option_rule，_fistword_jumpstrs】
        - _section_rule: 匹配section的正则表达式，匹配组名【section】
        - _option_rule: 匹配option的正则表达式，匹配组名【option，chain，value，prefix，other】
        - _fistword_jumpstrs: list[] 每行的第一个字符在其中则跳过"""
        self._section_rule = r"\[(?P<section>.*[^\s])\]"
        self._option_rule = r"(?P<prefix>)(?P<option>.*[^\s])(?P<chain>\s*=\s*)(?P<value>.*[^\s])(?P<other>\s*)"
        self._fistword_jumpstrs = ["\n",";"]

    def init_configs(self):
        """初始化，获取文件配置内容"""
        self.init_config_rule()
        
        section_name = "default"
        with open(self.path,'r') as fp:
            for index,line in enumerate(fp.readlines()):
                if line[0] in self._fistword_jumpstrs:
                    continue
                
                if tmp_section_name := re.search(self._section_rule,line):
                    section_name = tmp_section_name.group("section")
                    self._configs[section_name] = {}
                
                if tmp_option := re.search(self._option_rule,line):
                    option = tmp_option.group("option")
                    value = tmp_option.group("value")
                    chain = tmp_option.group("chain")
                    prefix = tmp_option.group("prefix")
                    other = tmp_option.group("other")
                    
                    self._index_to_location[index] = [section_name,option]
                    self._configs[section_name][option] = entry(option,value,index,chain,prefix,other)

                    
    def sections(self) -> list[str]:
        '''返回配置组名'''
        return self._configs.keys()
    
    def set_config(self,sec:str = "default",opt:str=None,val=None):
        '''设置配置项
        - sec: section
        - opt: option
        - val: value
        '''
        self._configs[sec][opt].value = str(val).lower()
        self._change_index.update([self._configs[sec][opt].index])
        
    def save(self):
        """保存文件，简单粗暴的设置方法（指正：替换方法）"""
        with open(self.path,"r") as fp:
            lines = fp.readlines()
        
        with open(self.path,"w") as wp:
            try:
                for i in list(self._change_index):
                    sec,opt = self.get_location(i)
                    lines[i] = str(self.get_entry(sec,opt))
            finally:
                for i in lines:
                    wp.write(i)
                    
    def get_config(self,sec:str,opt:str) -> str:
        """- sec: section
        - opt: option_
        """
        return self._configs[sec][opt].value

    def get_entry(self,sec:str,opt:str) -> entry:
        """- sec: section
        - opt: option_"""
        return self._configs[sec][opt]
        
    def get_section(self,sec:str) -> dict[str,entry]:
        return self._configs[sec]
    
    def get_location(self,index:int) -> list[str]:
        """通过索引获取section 和 option的名称"""
        return self._index_to_location[index]
        
class cfg_config(ini_config):
    def __init__(self, path) -> None:
        super().__init__(path)
        
    def init_config_rule(self):
        self._section_rule = r"(?P<section>.*[^\s])\s*\{"
        self._option_rule = r"(?P<prefix>\s*\w:)(?P<option>.*[^\s])(?P<chain>\s*=\s*)(?P<value>.*[^\s])(?P<other>\s*)"
        self._fistword_jumpstrs = ["\n","#"]

class txt_config(ini_config):
    def __init__(self, path) -> None:
        super().__init__(path)
    
    def init_config_rule(self):
        self._section_rule = r"\[(?P<section>.*[^\s])\]"
        self._option_rule = r"(?P<prefix>)(?P<option>.*[^\s])(?P<chain>\s*:\s*)(?P<value>.*[^\s])(?P<other>\s*)"
        self._fistword_jumpstrs = ["\n","/"]

class json_config:
    def __init__(self, path) -> None:
        self.path = path
        self._configs:dict = load(open(self.path))
    
    def set_config(self,sec:str | tuple,opt:str,value:Any):
        """设置配置项"""
        option = self.get_config(sec)
        option[opt] = value
    
    def save(self):
        with open(self.path,"w",encoding="utf-8") as fp:
            fp.write(dumps(self._configs,indent=4))
        
    def get_config(self,sec:str | tuple) -> Any:
        """获取配置项值"""
        if isinstance(sec,str):
            return self._configs[sec]
        elif isinstance(sec,tuple):
            tmp = self._configs
            for key in sec:
                tmp = tmp[key]
            return tmp
        
class Config:
    '''ini或者cfg的配置文件读取与修改'''
    def __init__(self,path:str) -> None:
        if isfile(path):
            self.path=path
            self.file_type=FileManage(file_path=self.path).file_type
        else:
            raise ValueError("文件路径错误")
    
    @property
    def Config(self):
        match self.file_type:
            case "ini":
                return ini_config(self.path)
            case "cfg":
                return cfg_config(self.path)
            case "txt":
                return txt_config(self.path)
            case "json":
                return json_config(self.path)
            case _:
                raise ValueError("文件不支持")

class FileManage:
    def __init__(self,work_path=None,file_path:str=None) -> None:
        if not work_path:
            self.work_path=getcwd()
        else:
            self.work_path=work_path
            if not exists(work_path):
                makedirs(work_path,exist_ok=True)
        if file_path:
            file_infor=splitext(file_path)
            self.file_path=file_path
            self.save_path=dirname(file_path)
            self.file_name=basename(file_path)
            self.file_type=file_infor[-1][1:]
    
    @staticmethod
    def nr_mv(old_path,new_path):
        '''not root move'''
        if not exists(new_path):
            shutil.move(old_path,new_path)
        else:
            FileManage.cp(old_path,new_path)
            FileManage.rm(old_path)
    
    @staticmethod
    def mv(old_path,new_path):
        if isdir(old_path):
            dir=split_path(old_path)[-1]
            new_path=join(new_path,dir)
        FileManage.nr_mv(old_path,new_path)
        
    @staticmethod
    def cp(main_path,aim_path):
        if isdir(main_path):
            shutil.copytree(main_path,aim_path,dirs_exist_ok=True)
        if isfile(main_path):
            shutil.copy(main_path,aim_path)
    
    @staticmethod
    def rm(path):
        if isdir(path):
            shutil.rmtree(path)
        if isfile(path):
            unlink(path)
    
    @staticmethod
    def touch(file_path:str,content = None):
        wp = FileManage(file_path=file_path).save_path
        if not exists(wp):
            makedirs(wp,exist_ok=True)
        if not exists(file_path):
            with open(file_path,"w") as fp:
                fp.write(content)

    def unzip(self,file_path,save_path=None,retain:bool=True) ->str:
        args = (file_path,save_path,retain)
        match FileManage(file_path = file_path).file_type:
            case "zip":
                return self.__unzip(*args)
            case "7z":
                return self.__un7zip(*args)
            case _ as x:
                raise ValueError(f"文件类型 {x} 错误")
    
    def __unzip(self,file_path:str,save_path:str = None,retain:bool = True):
        file=ZipFile(file_path)
        if not save_path:
            save_path=relpath(self.work_path,getcwd())
        file_list = file.namelist()
        pd = progress_bar(max=len(file_list),title=f"解压 {relpath(file_path,getcwd())} => {save_path}")
        for index,unzipfile in enumerate(file_list):
            file_info = file.getinfo(unzipfile)
            file_info.filename = self.redecode(file_info.filename)
            file.extract(file_info,save_path)
            pd.show(index+1)
            
        unzip_file_path=join(self.work_path,file_list[0][:-1])
        if not retain:
            del file
            self.rm(file_path)
        return unzip_file_path
    
    def __un7zip(self,file_path:str,save_path:str = None,retain:bool = True):
        file = SevenZipFile(file_path)
        if not save_path:
            save_path=relpath(self.work_path,getcwd())
        file_list = file.getnames()
        pd = progress_bar(max=len(file_list),title=f"解压 {relpath(file_path,getcwd())} => {save_path}")
        file.extractall(save_path)
        pd.finish()
    
        unzip_file_path=join(self.work_path,file_list[0][:-1])
        if not retain:
            del file
            self.rm(file_path)
        return unzip_file_path
        
    @staticmethod
    def redecode(raw:str) -> str:
        """重新编码，防止中文乱码"""
        try:
            return raw.encode('cp437').decode('gbk')
        except:
            return raw.encode('utf-8').decode('utf-8')
    
    @staticmethod
    def save(content:bytes,save_file_path:str=None):
        with open(save_file_path,"wb") as fp:
            fp.write(content)
    
    @staticmethod
    def rename(src,dst):
        rename(src,dst)
    
    def tree(self) ->list[str]:
        """显示所有文件及其附属文件的路径"""
        return [join(dirpath,file) for dirpath,dirnames,filenames in walk(self.work_path) for file in filenames]
    
    def ls(self) ->list[str]:
        """列出文件"""
        return listdir(self.work_path)
    
    def lsdir(self) -> list[str]:
        """列出文件路径"""
        return [join(self.work_path,path) for path in listdir(self.work_path)]
        
class url_manage:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def dowload(d_url:str,save_path=None,file_name=None) ->str:
        '''默认保存在当前工作目录 返回file_path'''
        if proxy:
            proxies = {"http":f"http://127.0.0.1:{proxy}"}
        if not save_path:
            save_path=getcwd()
        if not file_name:
            file_name=d_url.split("/")[-1]
        if not proxy:
            response = requests.get(d_url,headers=header,stream=True)
        else:
            response = requests.get(d_url,headers=header,stream=True,proxies=proxies)
        
        save_file_path=join(save_path,file_name)
        content_max = int(response.headers['content-length'])
        rf = progress_bar(content_max,f"下载 {file_name}")
        data = bytes()
        if response.ok:
            ...
        else:
            raise ConnectionError(d_url)
        for chunk in response.iter_content(1024*1024):
            data += chunk
            rf.show(len(data))
        FileManage(save_path).save(data,save_file_path)
        return save_file_path

class progress_bar:
    def __init__(self,max:int = 1,title:str=None,progress_item:str="■") -> None:
        if max == 0:
            max = 1
        self._max=max
        if max >= 1024:
            self.mode = "dowload"
        else:
            self.mode = "normal"
        self.title=title
        self._progress_item=progress_item
        self.max_len = get_terminal_size().columns - 1
        self.title_max_len = 54
        if wcswidth(self.title) >= 54:
            self.title = self.title[:45] + "..."

        self.show(0)
    
    def store(self,byte:int) -> str:
        unit="B"
        if byte>1024:
            byte>>=10
            unit="KB"
        if byte>1024:
            byte>>=10
            unit="MB"
        return f"""{byte} {unit}"""
    
    def show(self,value,title=None):
        if not title:
           title = self.title 
        proportion=int(value/self._max*20)
        space_len = self.title_max_len - wcswidth(title)
        if space_len < 0:   space_len = 0
        space_str = " "*space_len
        if self.mode == "normal":
            if proportion == 20:
                line = f"{title} :{space_str}"+"\t【{:<20}】 ✅".format(self._progress_item*proportion)
                print(line)
            else:
                line = f"{title} :{space_str}"+"\t【{:<20}】   ".format(self._progress_item*proportion)
                print(" "*self.max_len+"\r"+line,end="\r")
        elif self.mode == "dowload":
            if proportion == 20:
                line = f"{title} :{space_str}"+"\t【{:<20}】 ✅ titol {}".format(self._progress_item*proportion,self.store(value))
                print(line)
            else:
                line = f"{title} :{space_str}"+"\t【{:<20}】    titol {}".format(self._progress_item*proportion,self.store(value))
                print(" "*self.max_len+"\r"+line,end="\r")

    def finish(self):
        self.show(self._max)

class GTNH:
    @staticmethod
    def dowload_GTNH(url:str):
        urls = requests.get(url=url,headers=header).text.split()
        versions = [i.split("/")[-1] for i in urls]
        num = int(input("请选择安装版本：\n\t"+"\n\t".join([f"- {index+1}，{ver}" for index,ver in enumerate(versions)])+"\n"))
        file_path = url_manage.dowload(d_url=urls[num-1],file_name=versions[num-1])
        fm = FileManage()
        fm.unzip(file_path=file_path,retain=False)

    @staticmethod
    def set_eula():
        '''设置为同意eula协议'''
        eula_path = join(getcwd(),"eula.txt")
        eu_p = progress_bar(1,"同意eula协议")
        with open(eula_path,"w") as fp:
            fp.write("eula=true")
        eu_p.show(1)

    @staticmethod
    def set_file(mode:Literal["client","server"]):
        """使用配置设置文件"""
        configs = {'默认配置[模组，配置，材质，数据，汉化]':DEFAULT_CONFIG,
                   "默认配置[汉化]":DEFAULT_CHINESE_CONFIG}
        type = int(input("请选择配置：\n\t"+"\n\t".join([f"- {i+1}，{k}" for i,k in enumerate(configs.keys())])+"\n"))
        match mode:
            case "client":
                for config in configs[list(configs.keys())[type-1]]:
                    FileType(config).action()
            case "server":
                for config in configs[list(configs.keys())[type-1]]:
                    ft = FileType(config)
                    if ft.server_detail:
                        ft.action()

    @staticmethod
    def version():
        global NOW_VERSION
        if NOW_VERSION:
            return NOW_VERSION
        else:
            for file in FileManage().ls():
                if matcher := re.search(r"changelog.*to (?P<version>.*)\.md",file):
                    NOW_VERSION = matcher.group("version")
                    return NOW_VERSION
            else:
                print("未找到version，是否已安装GTNH？")
                system("pause")
                quit()
                    
def quit_script(x):
    ...

def main():
    mode = int(input('''选择模式：
        - 1，客户端
        - 2，服务端\n'''))
    match mode:
        case 1:
            type=int(input('''本脚本不会进行操作存档文件，可以设置，但建议手动转移，\n请选择模式：
        - 1，安装GTNH
        - 2，使用配置设置私货，设置配置文件
        - 3，1+2 安装+配置\n'''))
            match type:
                case 1:
                    GTNH.dowload_GTNH(client_url)
                case 2:
                    GTNH.set_file("client")
                case 3:
                    GTNH.dowload_GTNH(client_url)
                    GTNH.set_file("client")
                case _ as x:
                    quit_script(x)
        case 2:
            type = int(input('''请选择模式：
        - 1，部署服务端
        - 2，使用配置设置私货，设置配置文件
        - 3，1+2 部署+配置\n'''))
            match type:
                case 1:
                    GTNH.dowload_GTNH(server_url)
                    GTNH.set_eula()
                case 2:
                    GTNH.set_file("server")
                case 3:
                    GTNH.dowload_GTNH(server_url)
                    GTNH.set_file("server")
                    GTNH.set_eula()
                case _ as x:
                    quit_script(x)
        case _ as x:
            quit_script(x)

if __name__ == "__main__":
    main()
    system("pause")