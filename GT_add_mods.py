from os.path import isfile,splitext,isdir,basename,dirname,exists
from os.path import join as join_path
from os.path import split as split_path
from os import unlink,getcwd,rename,walk
from zipfile import ZipFile
from tkinter.filedialog import askdirectory
import re
import shutil
import requests

#DEFINE
proxy:int = None #代理端口
#删除的mod
rm_mods={
    'CraftPresence.jar':("discord相关",r"CraftPresence.*\.jar"),
    'defaultserverlist.jar':("默认添加的多人服务器",r"defaultserverlist.*\.jar"),
    'HardcoreDarkness-MC.jar':("更真实的黑暗",r"HardcoreDarkness-MC.*\.jar")
}
'''Use:
>>> {"方便记忆的模组文件名":("一句话介绍或者为None",“模组名称的正则表达式”)}'''

#添加的mod
add_mods={
    'Smooth Font':("平滑字体","https://mediafilez.forgecdn.net/files/2614/474/SmoothFont-1.7.10-1.15.3.jar"),
    'Twist Space Technolgy Mod':("扭曲空间科技","http://github.com/Nxer/Twist-Space-Technology-Mod/releases/download/0.4.30-2.6.1fitted-test-alpha/TwistSpaceTechnology-0.4.30-2.6.1fitted-test-alpha.jar"),
    'AromaBackup':("存档备份","https://mediafilez.forgecdn.net/files/2284/754/AromaBackup-1.7.10-0.1.0.0.jar"),
    'Aroma1997Core':("存档备份 前置","https://mediafilez.forgecdn.net/files/2257/644/Aroma1997Core-1.7.10-1.0.2.16.jar"),
    'inputfix':("中文输入修复","https://mediafilez.forgecdn.net/files/4408/526/InputFix-1.7.10-v6.jar"),
    'FpsReducer':("FPS减速器","https://mediafilez.forgecdn.net/files/2627/303/FpsReducer-mc1.7.10-1.10.3.jar"),
    'Extra Player Render':("额外玩家渲染","https://mediafilez.forgecdn.net/files/4287/440/extraplayerrenderer-1.7.10-1.0.1.jar"),
    #2.6版本自带相同功能，已弃用
    # 'NEI-Utilities':("NEI实用工具","https://github.com/RealSilverMoon/NEI-Utilities/releases/download/0.1.9/neiutilities-0.1.9.jar"),
    'Not Enough Characters':("NEI 拼音搜索","https://github.com/vfyjxf/NotEnoughCharacters/releases/download/1.7.10-1.5.2/NotEnoughCharacters-1.7.10-1.5.2.jar"),
    "NoFog":("移除所有雾","https://mediafilez.forgecdn.net/files/2574/985/NoFog-1.7.10b1-1.0.jar"),
    "OmniOcular":("根据方块NBT信息显示内容","https://mediafilez.forgecdn.net/files/2388/572/OmniOcular-1.7.10-1.0build103.jar"),
    'CustomSkinloader':("万用皮肤补丁14.6a",("https://modfile.mcmod.cn/action/download/?key=a1ca79539773703d72f73596f7af6e05","CustomSkinLoader_1.7.10-14.6a.jar")),
    'skinport':("支持纤细模型","https://mediafilez.forgecdn.net/files/3212/17/SkinPort-1.7.10-v10d.jar"),
    'WorldEdit':("创世神","https://mediafilez.forgecdn.net/files/2309/699/worldedit-forge-mc1.7.10-6.1.1-dist.jar"),
    'WorldEditCUIFe':("创世神UI forge版本","https://mediafilez.forgecdn.net/files/2390/420/WorldEditCuiFe-v1.0.7-mf-1.7.10-10.13.4.1566.jar"),
    'dualhotbar':("双倍快捷栏","https://mediafilez.forgecdn.net/files/2212/352/dualhotbar-1.7.10-1.6.jar")
}

#config目录下需修改的配置文件
set_configs={
    "fastcraft.ini":[("fastcraft配置文件 要与平滑字体兼容需修改配置","enableFontRendererTweaks","false")],
    "angelica-modules.cfg":[("安洁莉卡配置文件 防止平滑字体重影","enableFontRenderer","false")],
    ("aroma1997","AromaBackup.cfg"):[("存档配置文件 备份间隔","delay",1440),\
                                    ("存档配置文件 保持备份数量","keep",5),\
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
}

header={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
}

mods_path=join_path(getcwd(),"mods")
config_path=join_path(getcwd(),"config")

class entry:
    '''设置项的描述'''
    def __init__(self,conf,value,index:int,old:str,format:str='{conf} = {value}') -> None:
        self.conf=conf
        self.value=value
        self.index=index
        self.old=old
        self.format=format
    
    def __str__(self) -> str:
        return self.format.format(conf=self.conf,value=self.value)
    
class ini_config:
    '''ini文件实现，感觉不需要section'''
    def __init__(self,path) -> None:
        self.path=path
        self._index=0
        self.configs_index={}
        self.configs=self._configs()
        self.len=len(self.configs)
    
    def init_config_rule(self):
        self.config_rule='(\w{0,})\s{0,1}=\s{0,1}(\w{0,})'
        self.format_rule_conf="()\w*(\s?=)"
        self.format_rule_value="(=\s?)\w*()"
        
    def __iter__(self):
        return self
    
    def __next__(self) ->entry:
        if self._index < self.len:
            return_data=self.configs[self._index]
            self._index+=1
            return return_data
        else:
            self._index=0
            raise StopIteration
        
    def __getitem__(self,key) ->entry:
        return self.configs[self.configs_index[key]]
    
    @property
    def options(self) ->list[str]:
        '''返回设置项名称'''
        return [i.conf for i in self.configs]
    
    def _configs(self) ->list[entry]:
        self.init_config_rule()
        return_data:list[entry]=[]
        with open(self.path,'r') as fp:
            #return [entry(**self._read_line_config(value,index)) for index,value in enumerate(fp.readlines()) if self._read_line_config(value,index)]    
            for index,value in enumerate(fp.readlines()):
                if config_data:=self._read_line_config(value,index):
                    return_data.append(entry(**config_data))
                    self.configs_index[return_data[len(return_data)-1].conf]=len(return_data)-1
            return return_data
        
    def _read_line_config(self,line:str,index:int) ->dict | None:
        if line[0]==";" or line=='\n':
            return None
        config=re.findall(self.config_rule,line)
        if not config:
            return None
        format=re.sub(self.format_rule_conf,r"\1{conf}\2",re.sub(self.format_rule_value,r"\1{value}\2",line))
        return_data={
            "conf":config[0][0],
            "value":config[0][1],
            "index":index,
            "old":line,
            "format":format
        }
        return return_data
    
    def set_config(self,attr:str,value):
        '''设置配置项 简单粗暴的设置方法（指正：替换方法）'''
        with open(self.path,"r") as fp:
            lines=fp.readlines()
        with open(self.path,"w") as fp:
            try:
                item=self.__getitem__(attr)
                item.value=value
                lines[item.index]=str(item)
            finally:
                for i in lines:
                    fp.write(i)
    
    def get_config(self,key):
        return self.__getitem__(key).value 

class cfg_config(ini_config):
    def __init__(self, path) -> None:
        super().__init__(path)
        
    def init_config_rule(self):
        self.config_rule='''\w\s?:"?\s?([\w\s]+)"?\s?=\s?(\w*)'''
        self.format_rule_conf='''(\s+\w\s?:"?)[\w\s]+()'''
        self.format_rule_value='''("?\s?=\s?)\w*()'''
    
class Config:
    '''ini或者cfg的配置文件读取与修改'''
    def __init__(self,path:str) -> None:
        if isfile(path):
            self.path=path
            self.file_type=file_manage(file_path=self.path).file_type
        else:
            raise ValueError("文件路径错误")
            
    @property
    def config(self) ->ini_config | cfg_config:
        if self.file_type=="ini":
            return ini_config(self.path)
        elif self.file_type=="cfg":
            return cfg_config(self.path)

class file_manage:
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
    
    def nr_mv(self,old_path,new_path):
        '''not root move'''
        if not exists(new_path):
            shutil.move(old_path,new_path)
        else:
            self.cp(old_path,new_path)
            self.rm(old_path)
    
    def mv(self,old_path,new_path):
        if isdir(old_path):
            dir=split_path(old_path)[-1]
            new_path=join_path(new_path,dir)
        self.nr_mv(old_path,new_path)
        
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
        unzip_file_path=join_path(self.work_path,file.namelist()[0][:-1])
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
        return [join_path(dirpath,file) for dirpath,dirnames,filenames in walk(self.work_path) for file in filenames]
    
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
        save_file_path=join_path(save_path,file_name)
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
            raise ConnectionError()
        for chunk in response.iter_content(1024):
            data += chunk
            rf.show(len(data))
        file_manage.save(data,save_file_path)
        return save_file_path


class progress_bar:
    def __init__(self,max:int,title:str=None,progress_item:str="■") -> None:
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
        if title:
           self.title=title 
        proportion=int(value/self._max*20)
        if self.mode == "normal":
            if proportion == 20:
                print(f" {self.title} :","\t【{:<20}】 complete".format(self._progress_item*proportion))
            else:
                print(f" {self.title} :","\t【{:<20}】".format(self._progress_item*proportion),end="\r")
        elif self.mode == "dowload":
            if proportion == 20:
                print(f" {self.title} :"+"\t【{:<20}】titol {} complete".format(self._progress_item*proportion,self.store(value)))
            else:
                print(f" {self.title} :"+"\t【{:<20}】titol {}".format(self._progress_item*proportion,self.store(value)),end="\r")

def conf_join_path(main_path,args:str | tuple):
    if isinstance(args,tuple):
        return join_path(main_path,*args)
    else:
        return join_path(main_path,args)

#2.6版本官方自带汉化，已弃用
# def set_chinese_file():

def dowload_GTNH():
    urls = requests.get(url="http://downloads.gtnewhorizons.com/ClientPacks/?raw",headers=header).text.split()
    versions = [i.split("/")[-1] for i in urls]
    num = int(input("请选择安装版本：\n\t"+"\n\t".join([f"{index+1},{ver}" for index,ver in enumerate(versions)])+"\n"))
    file_path = url_manage.dowload(d_url=urls[num-1],file_name=versions[num-1])
    fm = file_manage()
    fm.unzip(file_path=file_path,retain=False)

def dowload_mods():
    for name,infor in add_mods.items():
        url,file_name=infor[-1],None
        if isinstance(url,tuple):
            url=url[0]
            file_name=url[-1]
        url_manage.dowload(url,mods_path,file_name)
    
def rm_file():
    '''删除不需要的文件或者模组'''
    for name,infor in rm_mods.items():
        rf_p=progress_bar(1,"删除mod")
        rule=infor[-1]
        fm=file_manage(mods_path)
        for i in fm.ls():
            if re.findall(rule,i):
                fm.rm(i)
        rf_p.show(1,f"删除mod【{name}】")
        
def set_config():
    for name,config in set_configs.items():
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
    fm=file_manage()
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
        
def main():
    type=int(input(\
        '''
        本脚本不会进行操作存档文件，可以设置，但建议手动转移
        请选择模式，
        1，安装GTNH
        2，（请在运行并结束GTNH生成配置文件后再运行）设置私货，配置文件，下载材质包
        请输入编号：'''
        ))
    if type not in range(1,6):
        raise ValueError("输入参数错误")
    if type == 1:
        dowload_GTNH()
    elif type == 2:
        rm_file()
        dowload_mods()
        # set_chinese_file()
        set_config()
        action_other_file()
    elif type == 3:
        '''设置配置文件'''
        set_config()
    elif type == 4:
        ''''其他文件的修改'''
        action_other_file()
    elif type == 5:
        '''汉化文件下载'''
        # set_chinese_file()

if __name__ == "__main__":
    main()