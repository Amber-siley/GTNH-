from os.path import isfile,splitext,isdir,basename,dirname,exists
from os.path import join as join_path
from os import unlink,getcwd,rename,walk
from zipfile import ZipFile
import re
import shutil
import requests

#DEFINE
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
    'Twist Space Technolgy Mod':("扭曲空间科技","https://github.com/Nxer/Twist-Space-Technology-Mod/releases/download/0.4.15-2.5.1fitted/TwistSpaceTechnology-0.4.15-2.5.1fitted.jar"),
    'AromaBackup':("存档备份","https://mediafilez.forgecdn.net/files/2284/754/AromaBackup-1.7.10-0.1.0.0.jar"),
    'Aroma1997Core':("存档备份 前置","https://mediafilez.forgecdn.net/files/2257/644/Aroma1997Core-1.7.10-1.0.2.16.jar"),
    'inputfix':("中文输入修复","https://mediafilez.forgecdn.net/files/4408/526/InputFix-1.7.10-v6.jar"),
    'FpsReducer':("FPS减速器","https://mediafilez.forgecdn.net/files/2627/303/FpsReducer-mc1.7.10-1.10.3.jar"),
    'NEI-Utilities':("NEI实用工具","https://github.com/RealSilverMoon/NEI-Utilities/releases/download/0.1.9/neiutilities-0.1.9.jar"),
    'Not Enough Characters':("NEI 拼音搜索","https://github.com/vfyjxf/NotEnoughCharacters/releases/download/1.7.10-1.5.2/NotEnoughCharacters-1.7.10-1.5.2.jar"),
    "NoFog":("移除所有舞","https://mediafilez.forgecdn.net/files/2574/985/NoFog-1.7.10b1-1.0.jar"),
    "OmniOcular":("根据方块NBT信息显示内容","https://mediafilez.forgecdn.net/files/4475/975/OmniOcular-1.7.10-1.0-java8%2C17-20.jar"),
}

#修改的配置文件
set_configs={
    "fastcraft.ini":("fastcraft配置文件 要与平滑字体兼容需修改配置","enableFontRendererTweaks","false"),
    
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
    
    def mv(self,old_path,new_path):
        if not exists(new_path):
            shutil.move(old_path,new_path)
        else:
            self.cp(old_path,new_path)
            self.rm(old_path)
    
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
    def dowload(d_url:str,save_path=None) ->str:
        '''默认保存在当前工作目录'''
        if not save_path:
            save_path=getcwd()
        file_name=d_url.split("/")[-1]
        save_file_path=join_path(save_path,file_name)
        file=requests.get(d_url,headers=header).content
        file_manage.save(file,save_file_path)
        return save_file_path

class progress_bar:
    def __init__(self,max:int,title:str=None,progress_item:str="■") -> None:
        self._max=max
        self.title=title
        self._progress_item=progress_item
        self.show(0)
    
    def show(self,value,title=None):
        if title:
           self.title=title 
        proportion=int(value/self._max*20)
        if proportion == 20:
            print(f" {self.title} :","\t【{:<20}】 complete".format(self._progress_item*proportion))
        else:
            print(f" {self.title} :","\t【{:<20}】".format(self._progress_item*proportion),end="\r")
    
def set_chinese_file():
    scf_p=progress_bar(5,"汉化文件安装")
    fm=file_manage()
    file_path=url_manage.dowload("https://github.com/Kiwi233/Translation-of-GTNH/archive/refs/heads/master.zip")
    scf_p.show(1)
    file_path=fm.unzip(file_path,retain=False)
    scf_p.show(2)
    del_item=[".github","scripts",".gitignore","zh_CN_GT5.09.32pre6.lang","LICENSE"]
    for i in del_item:
        del_path=join_path(file_path,i)
        fm.rm(del_path)
    scf_p.show(3)
    config=join_path(file_path,"config")
    resources=join_path(file_path,"resources")
    txloader=join_path(config,"txloader")
    forceload=join_path(txloader,"forceload")
    fm.mv(resources,forceload)
    scf_p.show(4)
    fm.mv(file_path,getcwd())
    scf_p.show(5)
    
def dowload_mods():
    for name,infor in add_mods.items():
        add_p=progress_bar(1,"添加mod")
        url=infor[-1]
        fm=file_manage(mods_path)
        url_manage.dowload(url,mods_path)
        add_p.show(1,f"下载mod {name} ")
    
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
        fg_p=progress_bar(1,"配置文件")
        config_file=join_path(config_path,name)
        cg=Config(config_file).config
        cg.set_config(config[-2],config[-1])
        fg_p.show(1,f"配置文件 {name}.{config[-2]} ")

def main():
    type=int(input(\
        "请选择模式,推荐先使用1下载和删除文件运行游戏后,关闭游戏,再执行模式2\n\
            1 :下载模组,删除不必要的文件\n\
            2 :修改配置文件\n\
        请输入编号："
        ))
    if type not in (1,2):
        raise ValueError("输入参数错误")
    if type == 1:
        rm_file()
        dowload_mods()
        set_chinese_file()
    else:
        set_config()
        
main()