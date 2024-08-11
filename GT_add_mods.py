from os.path import isfile,splitext,isdir,basename,dirname,exists,join
from os.path import split as split_path
from os import unlink,getcwd,rename,walk,system
from zipfile import ZipFile
from tkinter.filedialog import askdirectory
from abc import abstractmethod
from copy import deepcopy
from typing import Literal,Any

import re
import shutil
import requests

#DEFINE
proxy:int = None #代理端口
#删除的mod
rm_mods = {
    'CraftPresence.jar':("discord相关",r"CraftPresence.*\.jar"),
    'defaultserverlist.jar':("默认添加的多人服务器",r"defaultserverlist.*\.jar"),
    'HardcoreDarkness-MC.jar':("更真实的黑暗",r"HardcoreDarkness-MC.*\.jar")
}
'''Use:
>>> {"方便记忆的模组文件名":("一句话介绍或者为None",“模组名称的正则表达式”)}'''

server_rm_mods = {
    'HardcoreDarkness-MC.jar':("更真实的黑暗",r"HardcoreDarkness-MC.*\.jar")
}
#添加的mod
add_mods = {
    'Smooth Font':("平滑字体","https://mediafilez.forgecdn.net/files/2614/474/SmoothFont-1.7.10-1.15.3.jar"),
    'Twist Space Technolgy Mod':("扭曲空间科技","http://github.com/Nxer/Twist-Space-Technology-Mod/releases/download/0.4.30-GTNH2.6.1/TwistSpaceTechnology-0.4.30-GTNH2.6.1.jar"),
    'ZeroPointBugfix':("零点错误修复","https://github.com/wohaopa/ZeroPointServerBugfix/releases/download/0.6.3/ZeroPointBugfix-0.6.3.jar"),
    # 2.6版本ServerUtilities已自带相关功能，已弃用
    # 'AromaBackup':("存档备份","https://mediafilez.forgecdn.net/files/2284/754/AromaBackup-1.7.10-0.1.0.0.jar"),
    # 'Aroma1997Core':("存档备份 前置","https://mediafilez.forgecdn.net/files/2257/644/Aroma1997Core-1.7.10-1.0.2.16.jar"),
    
    # 2.6版本零点错误修复已内置该功能，已弃用
    # 'inputfix':("中文输入修复","https://mediafilez.forgecdn.net/files/4408/526/InputFix-1.7.10-v6.jar"),
    'FpsReducer':("FPS减速器","https://mediafilez.forgecdn.net/files/2627/303/FpsReducer-mc1.7.10-1.10.3.jar"),
    'Extra Player Render':("额外玩家渲染","https://mediafilez.forgecdn.net/files/4287/440/extraplayerrenderer-1.7.10-1.0.1.jar"),
    # 2.6版本自带相同功能，已弃用
    # 'NEI-Utilities':("NEI实用工具","https://github.com/RealSilverMoon/NEI-Utilities/releases/download/0.1.9/neiutilities-0.1.9.jar"),
    'Not Enough Characters':("NEI 拼音搜索","http://github.com/vfyjxf/NotEnoughCharacters/releases/download/1.7.10-1.5.2/NotEnoughCharacters-1.7.10-1.5.2.jar"),
    "NoFog":("移除所有雾","https://mediafilez.forgecdn.net/files/2574/985/NoFog-1.7.10b1-1.0.jar"),
    "OmniOcular":("根据方块NBT信息显示内容","https://mediafilez.forgecdn.net/files/2388/572/OmniOcular-1.7.10-1.0build103.jar"),
    'CustomSkinloader':("万用皮肤补丁14.6a",("https://modfile.mcmod.cn/action/download/?key=a1ca79539773703d72f73596f7af6e05","CustomSkinLoader_1.7.10-14.6a.jar")),
    # 与皮肤补丁似乎功能重复了，已弃用
    # 'skinport':("支持纤细模型","https://mediafilez.forgecdn.net/files/3212/17/SkinPort-1.7.10-v10d.jar"),
    'WorldEdit':("创世神","https://mediafilez.forgecdn.net/files/2309/699/worldedit-forge-mc1.7.10-6.1.1-dist.jar"),
    'WorldEditCUIFe':("创世神UI forge版本","https://mediafilez.forgecdn.net/files/2390/420/WorldEditCuiFe-v1.0.7-mf-1.7.10-10.13.4.1566.jar"),
    # 与苹果皮有点UI重合，已弃用
    # 'dualhotbar':("双倍快捷栏","https://mediafilez.forgecdn.net/files/2212/352/dualhotbar-1.7.10-1.6.jar")
}

#服务器添加mod
server_add_mods = {
    'Twist Space Technolgy Mod':("扭曲空间科技","https://github.com/Nxer/Twist-Space-Technology-Mod/releases/download/0.4.30-GTNH2.6.1/TwistSpaceTechnology-0.4.30-GTNH2.6.1.jar"),
    # 2.6版本ServerUtilities已自带相关功能，已弃用
    # 'AromaBackup':("存档备份","https://mediafilez.forgecdn.net/files/2284/754/AromaBackup-1.7.10-0.1.0.0.jar"),
    # 'Aroma1997Core':("存档备份 前置","https://mediafilez.forgecdn.net/files/2257/644/Aroma1997Core-1.7.10-1.0.2.16.jar"),
    
    # oo配置文件服务器也需装
    "OmniOcular":("根据方块NBT信息显示内容","https://github.com/wohaopa/OmniOcular-Unofficial/releases/download/1.5.1/OmniOcularUnofficial-1.5.1.jar"),
    'WorldEdit':("创世神","https://mediafilez.forgecdn.net/files/2309/699/worldedit-forge-mc1.7.10-6.1.1-dist.jar")
}

#config目录下需修改的配置文件
set_configs = {
    "fastcraft.ini":[("fastcraft配置文件 要与平滑字体兼容需修改配置","enableFontRendererTweaks","false")],
    "angelica-modules.cfg":[("安洁莉卡配置文件 防止平滑字体重影","enableFontRenderer","false")],
    
    # ("aroma1997","AromaBackup.cfg"):[("存档配置文件 备份间隔","delay",360),\
    #                                 ("存档配置文件 保持备份数量","keep",5),\
    #                                 ("存档配置文件 打开存档时备份","onStartup","false"),\
    #                                 ("存档配置文件 压缩率","compressionRate",9)]
}

#服务器config目录下修改的配置文件
server_set_configs = {
    ("aroma1997","AromaBackup.cfg"):[("存档配置文件 备份间隔","delay",360),\
                                    ("存档配置文件 保持备份数量","keep",7),\
                                    ("存档配置文件 打开存档时备份","onStartup","false"),\
                                    ("存档配置文件 压缩率","compressionRate",9)]
}

#其他 文件或者文件夹
other_file={
    'options.txt':
        {
            'type':"local",             #文件类型，本地文件local or 网络文件online
            'url':None,                 #下载网址，当为online文件时有意义，None无意义
            'file_name':None,           #通过网络下载文件url中无文件名时需定义
            'description':"游戏按键设置文件",#介绍
            'need_unzip':False,         #是否需要解压操作
            'retain_zip':True,          #是否保留zip文件
            'action_type':'copy',       #执行的类型，复制copy，完整移动move，不包含主目录移动nr_move
            'save_location':None        #复制的保存路径，None表示脚本当前工作目录
        },
    'optionsof.txt':
        {
            'type':'local',
            'url':None,
            'file_name':None,
            'description':"游戏视频设置文件",
            'need_unzip':False,
            'retain_zip':True,
            'action_type':'copy',
            'save_location':None
        },
    ('journeymap','data'):
        {
            'type':'local',
            'url':None,
            'file_name':None,
            'description':"旅行地图数据文件",
            'need_unzip':False,
            'retain_zip':True,
            'action_type':'copy',
            'save_location':('journeymap','data')
        },
    ('journeymap','config'):
        {
            'type':'local',
            'url':None,
            'file_name':None,
            'description':"旅行地图配置文件",
            'need_unzip':False,
            'retain_zip':True,
            'action_type':'copy',
            'save_location':('journeymap','config')
        },
    "visualprospecting":
        {
            'type':'local',
            'url':None,
            'file_name':None,
            'description':"矿脉，油田文件",
            'need_unzip':False,
            'retain_zip':True,
            'action_type':'copy',
            'save_location':"visualprospecting"
        },
    'GTNH-Faithful-Textures.0.9.6.zip':
        {
            'type':'online',
            'url':"http://github.com/Ethryan/GTNH-Faithful-Textures/releases/download/0.9.6/GTNH-Faithful-Textures.0.9.6.zip",
            'file_name':None,
            'description':"GTNH Faithful材质包 ",
            'need_unzip':False,
            'retain_zip':False,
            'action_type':'move',
            'save_location':'resourcepacks'
        },
    'OO':
        {
            'type':"online",
            "url":"",
        }
}

header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}

client_url = "http://downloads.gtnewhorizons.com/ClientPacks/?raw"
server_url = "http://downloads.gtnewhorizons.com/ServerPacks/?raw"

mods_path = join(getcwd(),"mods")
eula_path = join(getcwd(),"eula.txt")
config_path = join(getcwd(),"config")

class FileType:
    '''处理文件描述'''
    LOCAL = "local"
    ONLINE = "online"
    
    NR_MV = "nr_mv"
    MV = "mv"
    CP = "cp"
    RM = "rm"
    
    ATTR_ENABLED = "enabled"
    ATTR_DESC = "description"
    
    ATTR_FP = "file_path"
    ATTR_WP = "work_path"
    
    ATTR_RE_NAME = "regular_name"
    ATTR_FN = "file_name"
    
    ATTR_SP = "save_path"
    ATTR_TYPE = "type"
    ATTR_URL = "url"
    ATTR_UZIP = "unzip"
    ATTR_REZIP = "retain_zip"
    ATTR_ACTION = "action_type"
    ATTR_SCRIPT = "script"
    ATTR_VERSION_DEMAND = "version"
    ATTR_CONFIG_DEMAND = "config"
    
    def __init__(self, **kwargs:dict[str,dict[str,Any]]) -> None:
        self.enabled:bool = False
        self.file_path:str = None
        self.file_name:str = None
        self.save_path:tuple = None
        self.type:str = None
        self.description:str = None
        self.work_path:str = None
        self.regular_name:str = None
        self.url:str = None
        self.unzip:bool = False
        self.retain_zip:bool = True
        self.action_type:Literal["mv","nr_mv","cp","rm"] = None
        self.script:list = None
        for key,value in kwargs.items():
            self.__setattr__(key,value)
        if self.work_path == None and self.regular_name
    
    def join_path(self,main_path,args:str | tuple):
        if isinstance(args,tuple):
            return join(main_path,*args)
        else:
            return join(main_path,args)

    def action_local(self):
        if not self.enabled:
            return
        
        match self.action_type:
            #rm file
            case FileType.RM:
                pb = progress_bar(title=f"删除 {self.file_path} {self.description}")
                work = FileManage(work_path=self.work_path)
                files = work.ls()
                for path in files:
                    if re.findall(self.regular_name,FileManage(path).file_name):
                        work.rm(path)
                        break
                pb.finish()
            
            #mv file
            case FileType.MV:
                pb = progress_bar(title=f"移动 {self.file_path} -> {self.save_path}")
                
        
    def action_online(self):
        ...
        
    def action(self):
        match self.type:
            case FileType.LOCAL:
                self.action_local()
            case FileType.ONLINE:
                self.action_online()
            case _:
                ValueError("配置文件类型错误")
        
DEFAULT_CONFIG = [
    #删除的文件
    {
        FileType.ATTR_ENABLED:True,
        FileType.ATTR_TYPE:FileType.LOCAL,
        FileType.ATTR_DESC:"discord相关",
        FileType.ATTR_WP:"mods",
        FileType.ATTR_RE_NAME:r"CraftPresence.*\.jar",
        FileType.ATTR_ACTION:FileType.RM
    },
    {
        FileType.ATTR_ENABLED:True,
        FileType.ATTR_TYPE:FileType.LOCAL,
        FileType.ATTR_DESC:"默认添加的多人服务器",
        FileType.ATTR_WP:"mods",
        FileType.ATTR_RE_NAME:r"defaultserverlist.*\.jar",
        FileType.ATTR_ACTION:FileType.RM
    },
    {
        FileType.ATTR_ENABLED:True,
        FileType.ATTR_TYPE:FileType.LOCAL,
        FileType.ATTR_DESC:"更真实的黑暗",
        FileType.ATTR_WP:"mods",
        FileType.ATTR_RE_NAME:r"HardcoreDarkness-MC.*\.jar",
        FileType.ATTR_ACTION:FileType.RM
    }
]

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
        self.ini_configs()
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

    def ini_configs(self):
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
            case _:
                raise ValueError("文件不支持")

class FileManage:
    def __init__(self,work_path=None,file_path:str=None) -> None:
        if not work_path:
            self.work_path=getcwd()
        else:
            self.work_path=work_path
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
    
    def unzip(self,file_path,save_path=None,retain:bool=True) ->str:
        file=ZipFile(file_path)
        if not save_path:
            save_path=self.work_path
        file.extractall(save_path)
        unzip_file_path=join(self.work_path,file.namelist()[0][:-1])
        if not retain:
            del file
            self.rm(file_path)
        return unzip_file_path
    
    @staticmethod
    def save(content:bytes,save_file_path:str=None):
        with open(save_file_path,"wb") as fp:
            fp.write(content)
    
    @staticmethod
    def rename(src,dst):
        rename(src,dst)
    
    def ls(self) ->list[str]:
        return [join(dirpath,file) for dirpath,dirnames,filenames in walk(self.work_path) for file in filenames]
    
class url_manage:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def dowload(d_url:str,save_path=None,file_name=None) ->str:
        '''默认保存在当前工作目录'''
        if proxy:
            proxies = {"http":f"http://127.0.0.1:{proxy}"}
        if not save_path:
            save_path=getcwd()
        if not file_name:
            file_name=d_url.split("/")[-1]
        save_file_path=join(save_path,file_name)
        # file=requests.get(d_url,headers=header).content
        if not proxy:
            response = requests.get(d_url,headers=header,stream=True)
        else:
            response = requests.get(d_url,headers=header,stream=True,proxies=proxies)
        content_max = int(response.headers['content-length'])
        rf = progress_bar(content_max,f"下载文件 {file_name}")
        data = bytes()
        if response.ok:
            ...
        else:
            raise ConnectionError(d_url)
        for chunk in response.iter_content(1024*1024):
            data += chunk
            rf.show(len(data))
        FileManage.save(data,save_file_path)
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
        if self.mode == "normal":
            if proportion == 20:
                print(f" {title} :","\t【{:<20}】 complete".format(self._progress_item*proportion))
            else:
                print(f" {title} :","\t【{:<20}】".format(self._progress_item*proportion),end="\r")
        elif self.mode == "dowload":
            if proportion == 20:
                print(f" {title} :"+"\t【{:<20}】titol {} complete".format(self._progress_item*proportion,self.store(value)))
            else:
                print(f" {title} :"+"\t【{:<20}】titol {}".format(self._progress_item*proportion,self.store(value)),end="\r")

    def finish(self):
        self.show(self._max)
    
def conf_join_path(main_path,args:str | tuple):
    if isinstance(args,tuple):
        return join(main_path,*args)
    else:
        return join(main_path,args)

#2.6版本官方自带汉化，已弃用
# def set_chinese_file():

def dowload_GTNH(url:str):
    urls = requests.get(url=url,headers=header).text.split()
    versions = [i.split("/")[-1] for i in urls]
    num = int(input("请选择安装版本：\n\t"+"\n\t".join([f"- {index+1}，{ver}" for index,ver in enumerate(versions)])+"\n"))
    file_path = url_manage.dowload(d_url=urls[num-1],file_name=versions[num-1])
    fm = FileManage()
    fm.unzip(file_path=file_path,retain=False)

def dowload_mods(target:dict):
    '''- target 添加mod描述字典'''
    for name,infor in target.items():
        url,file_name=infor[-1],None
        if isinstance(url,tuple):
            url=url[0]
            file_name=url[-1]
        url_manage.dowload(url,mods_path,file_name)
    
def rm_file(target:dict):
    '''删除不需要的文件或者模组'''
    for name,infor in target.items():
        rf_p=progress_bar(1,"删除mod")
        rule=infor[-1]
        fm=FileManage(mods_path)
        for i in fm.ls():
            if re.findall(rule,i):
                fm.rm(i)
        rf_p.show(1,f"删除mod【{name}】")
        
def set_config(target:dict):
    '''- target 设置描述字典'''
    for name,config in target.items():
        config_file=conf_join_path(config_path,name)
        try:
            cg=Config(config_file).config
        except ValueError:
            continue
        for option in config:
            cg.set_config(option[-2],option[-1])
            fg_p=progress_bar(1,"配置文件")
            fg_p.show(1,f"配置文件 {name}.{option[-2]} ")

def action_other_file():
    print("请选择需要转移的文件的游戏根目录")
    old_path=askdirectory(title="请选择需要转移的文件的游戏根目录")
    if not old_path:
        return 0
    fm=FileManage()
    for file,conf in other_file.items():
        of_p=progress_bar(1,f"{conf['description']}")
        if conf["type"] == 'local':
            old_file_path=conf_join_path(old_path,file)
        elif conf["type"] == 'online':
            old_file_path=url_manage.dowload(conf["url"],file_name=conf["file_name"])
        if conf["need_unzip"]:
            old_file_path=fm.unzip(old_file_path,retain=conf["retain_zip"])
        if not conf['save_location']:
            conf["save_location"]=fm.work_path
        else:
            conf["save_location"]=conf_join_path(fm.work_path,conf["save_location"])
        if conf['action_type'] == 'copy':
            fm.cp(old_file_path,conf["save_location"])
        elif conf['action_type'] == 'move':
            fm.mv(old_file_path,conf["save_location"])
        elif conf["action_type"] == 'nr_move':
            fm.nr_mv(old_file_path,conf["save_location"])
        of_p.show(1)

def set_eula():
    '''设置为同意eula协议'''
    eu_p = progress_bar(1,"同意eula协议")
    with open(eula_path,"w") as fp:
        fp.write("eula=true")
    eu_p.show(1)

def main():
    mode = int(input('''选择模式：
            - 1，客户端
            - 2，服务端\n'''))
    match mode:
        case 1:
            type=int(input('''本脚本不会进行操作存档文件，可以设置，但建议手动转移，\n请选择模式：
            - 1，安装GTNH
            - 2，设置私货，下载材质包
            - 3，（请在运行并结束GTNH生成配置文件后再运行）设置配置文件\n'''))
            match type:
                case 1:
                    dowload_GTNH(client_url)
                case 2:
                    rm_file(rm_mods)
                    dowload_mods(add_mods)
                    # set_chinese_file()
                    set_config(set_configs)
                    action_other_file()
                case 3:
                    '''设置配置文件'''
                    set_config(set_configs)
                case 4:
                    ''''其他文件的修改'''
                    action_other_file()
                case 5:
                    '''汉化文件下载'''
                    # set_chinese_file()
                case _:
                    raise ValueError("参数错误")
        case 2:
            type = int(input('''请选择模式：
            - 1，部署服务端
            - 2，（请在运行并结束GTNH服务端后生成配置文件后再运行）设置配置文件\n'''))
            match type:
                case 1:
                    dowload_GTNH(server_url)
                    set_eula()
                    rm_file(server_rm_mods)
                    dowload_mods(server_add_mods)
                case 2:
                    set_config(server_set_configs)
                case _:
                    raise ValueError("参数错误")
        case _:
            raise ValueError("参数错误")
                    
if __name__ == "__main__":
    main()
    system("pause")