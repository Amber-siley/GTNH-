from os.path import isfile,splitext,isdir
from os import unlink
import re
import os
import shutil

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
    '''ini文件实现'''
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
            self.file_type=splitext(self.path)[-1][1:]
        else:
            raise ValueError("文件路径错误")
            
    @property
    def config(self) ->ini_config | cfg_config:
        return eval(f'{self.file_type}_config("{self.path}")')   

class file_manage:
    def __init__(self) -> None:
        pass
    def move(self,old_path,new_path):
        shutil.move(old_path,new_path)
    
    def copy(self,main_path,aim_path):
        if isdir(main_path):
            shutil.copytree(main_path,aim_path)
        if isfile(main_path):
            shutil.copy(main_path,aim_path)
    
    def rm(self,path):
        if isdir(path):
            shutil.rmtree(path)
        if isfile(path):
            unlink(path)
            
