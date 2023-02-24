# coding:utf-8
# Author:altman
import re
import requests
import pandas as pd
import function
from urllib import parse
from config import *
from logger import logger



class PocClustering:
    def __init__(self, poc_filename) -> None:
        self.te_name = TE_NAME
        self.poc_filename = poc_filename
        self.poc_list = []
        self.poc_location = []
        self.control_line = []
        self.tag_name = []
        self.poc_exec_path = []
        self.cluster_result = []
        self.fuzz_char = []
        self.get_poc_from_excel()
        self.get_tag_name()
        # self.get_execute_path()


    def get_poc_from_excel(self):
        data = pd.read_excel(self.poc_filename, sheet_name="Sheet1")
        data = data.values.tolist()
        for d in data:
            self.poc_list.append(parse.unquote(d[0]))
            self.poc_location.append(d[1])
            self.control_line.append(d[2])
            self.fuzz_char.append(d[3])


    def get_tag_name(self):
        if self.te_name == 'smarty':
            for poc in self.poc_list:
                tag_name = re.findall("{([a-z|_]*) [\s\S]*?}", poc)
                self.tag_name.append(tag_name)

        if self.te_name == 'latte':
            for poc in self.poc_list:
                tag_list = []
                tag_name = re.findall("{([a-z|_]*) [\s\S]*?}", poc)
                tag_list.extend(tag_name)
                function_name = re.findall("{([a-z|_]*?)\([\s\S]*?\)}", poc)
                tag_list.extend(function_name)
                filter_name = re.findall("{[\s\S]*?\|([a-zA-Z]*?)[=;:].*?}", poc)
                tag_list.extend(filter_name)
                filter_name2 = re.findall("{[\s\S]*?\|([a-zA-Z]*?)}", poc)
                tag_list.extend(filter_name2)
                self.tag_name.append(tag_list)

        if self.te_name == 'thinkphp':
            for poc in self.poc_list:
                tag_list = []
                tag_name = re.findall("{([a-z|_]*) [\s\S]*?}", poc)
                tag_list.extend(tag_name)
                function_name = re.findall("{([a-z|_]*?)\([\s\S]*?\)}", poc)
                tag_list.extend(function_name)
                filter_name = re.findall("{[\s\S]*?\|([a-zA-Z0-9]*?)[=;:].*?}", poc)
                tag_list.extend(filter_name)
                filter_name2 = re.findall("{[\s\S]*?\|([a-zA-Z0-9]*?)}", poc)
                tag_list.extend(filter_name2)
                self.tag_name.append(tag_list)

        if self.te_name == 'dwoo':
            for poc in self.poc_list:
                tag_list = []
                tag_name = re.findall("{([a-z|_]*) [\s\S]*?}", poc)
                tag_list.extend(tag_name)
                function_name = re.findall("{([a-z|_]*?)\([\s\S]*?\)}", poc)
                tag_list.extend(function_name)
                self.tag_name.append(tag_list)

        if self.te_name == 'mustache':
            for poc in self.poc_list:
                tag_list = []
                if re.match("{{\#[\s\S]*?}}[\s\S]*?{{\/[\s\S]*?}}", poc) or re.match(
                        "{{\^[\s\S]*?}}[\s\S]*?{{\/[\s\S]*?}}", poc):
                    self.tag_name.append(['#'])
                else:
                    tag_name = re.findall("{{[\s\S]*?}}", poc)
                    tag_list.extend(tag_name)
                    self.tag_name.append(tag_list)

        if self.te_name == 'fenom':
            for poc in self.poc_list:
                tag_list = []
                tag_name = re.findall("{([a-z|_]*) [\s\S]*?}", poc)
                tag_list.extend(tag_name)
                tag_name = re.findall("{'[\s\S]*?'([\s\S]*?)'[\s\S]*?'}", poc)
                tag_list.extend(tag_name)
                tag_name = re.findall("{[\s\S]*?\|([\s\S]*?)}", poc)
                tag_list.extend(tag_name)
                self.tag_name.append(tag_list)

    def get_cc_path(self):
        return BASE_TE_PATH + self.te_name + "coverage"

    def get_execute_path(self):
        for poc_s in self.poc_list:
            try:
                r = requests.get(url=function.get_te_url(self.te_name),
                                 params={'a': poc_s,
                                         "filename": str(self.poc_list.index(poc_s)) + ".txt"}, timeout=3)
            except BaseException as e:
                logger.info("Web System Error")
                logger.info(e)
            exec_path = self.get_cc_path() + str(self.poc_list.index(poc_s)) + ".txt"
            self.poc_exec_path.append(exec_path)
        return True

    def check_execute_path(self, id_1, id_2):
        execute_path_file_1, execute_path_file_2 = self.poc_exec_path[id_1], self.poc_exec_path[id_2]
        with open(execute_path_file_1, "r") as f:
            execute_path_1 = f.readlines()
        with open(execute_path_file_2, "r") as f:
            execute_path_2 = f.readlines()
        execute_path_1 = set(execute_path_1)
        execute_path_2 = set(execute_path_2)
        if execute_path_1 == execute_path_1:
            return 1
        elif execute_path_1.issubset(execute_path_2):
            return 2
        elif execute_path_2.issubset(execute_path_1):
            return 3
        else:
            return 0


    def check_tag_path(self, id_1, id_2):
        tag_1, tag_2 = self.tag_name[id_1], self.tag_name[id_2]
        tag_1 = set(tag_1)
        tag_2 = set(tag_2)
        if tag_1 == tag_2:
            return 1
        if tag_1.issubset(tag_2):
            return 2
        if tag_2.issubset(tag_1):
            return 3
        else:
            return 0


    def clustering_method_1(self):
        unique_id = 0
        tag_name_base = [[0, self.poc_list[0], self.tag_name[0], unique_id]]
        for index in range(1, len(self.poc_list)):
            insert_flag = False
            for index_unique in range(0, len(tag_name_base)):
                if self.check_tag_path(tag_name_base[index_unique][0], index) == self.check_execute_path(
                        tag_name_base[index_unique][0], index):
                    tag_name_base.append(
                        [index, self.poc_list[index], self.tag_name[index], tag_name_base[index_unique][3],
                         self.poc_location[index], self.control_line[index], self.fuzz_char[index]])
                    insert_flag = True
                    break
            if not insert_flag:
                unique_id = unique_id + 1
                tag_name_base.append(
                    [index, self.poc_list[index], self.tag_name[index], unique_id, self.poc_location[index],
                     self.control_line[index], self.fuzz_char[index]])
        return tag_name_base

    def clustering_method_2(self):
        unique_id = 0
        tag_name_base = [[0, self.poc_list[0], self.tag_name[0], unique_id, self.poc_location[0], self.control_line[0],
                          self.fuzz_char[0]]]
        for index in range(1, len(self.poc_list)):
            insert_flag = False
            for index_unique in range(0, len(tag_name_base)):
                if set(self.tag_name[tag_name_base[index_unique][0]]) == set(self.tag_name[index]):
                    tag_name_base.append(
                        [index, self.poc_list[index], self.tag_name[index], tag_name_base[index_unique][3],
                         self.poc_location[index], self.control_line[index], self.fuzz_char[index]])
                    insert_flag = True
                    break
            if not insert_flag:
                unique_id = unique_id + 1
                tag_name_base.append(
                    [index, self.poc_list[index], self.tag_name[index], unique_id, self.poc_location[index],
                     self.control_line[index], self.fuzz_char[index]])
        return tag_name_base



