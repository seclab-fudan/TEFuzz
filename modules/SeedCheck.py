import function
from urllib import parse
from Logger import logger
import pandas as pd
import requests
import tqdm
from modules import ErrorModeling
from config import *


class SeedCheck:

    def __init__(self) -> None:
        logger.info("[*]Seed check start")
        self.error_type_list = []
        self.error_info_list = []
        self.modeling_data = []
        self.normal_list = []
        self.modeling_list = []
        self.mutate_all = 0
        self.mutate_success = 0
        self.seed_file_name = ''
        self.index = 0
        self.r = None

    def set_seed_file_name(self, filename):
        self.seed_file_name = filename

    def get_seed_data(self):
        self.modeling_data = function.read_data_from_excel(SEED_LOG_PATH + self.seed_file_name, 0)

    def check_1(self):
        self.get_seed_data()
        logger.info("init seed number : " + str(len(self.modeling_data)))
        for i in tqdm.tqdm(range(0, len(self.modeling_data))):
            self.index = i
            try:
                r = requests.get(url=function.get_te_url(TE_NAME),
                                 params={'a': self.modeling_data[i],
                                         "filename": "seed1.txt"}, timeout=3)
                function.clean_te_cache(TE_NAME)
                self.r = r
            except BaseException as e:
                logger.info("Web System Error")
                logger.info(e)
                continue
            if self.content_analysis() == 0:
                continue
            elif self.content_analysis() == 1:
                if self.func_1() == 0: continue
            else:
                self.normal_list.append(self.modeling_data[i])
        logger.info("normal seed number : " + str(len(self.normal_list)))
        self.save()

    def content_analysis(self):
        if "xdebug-error" in self.r.text:
            error_type, error_info = function.catch_error(self.r.text)
            if error_type.__len__() == 1 and error_type[0] == 'Warning':
                return 0
            else:
                return 1
        else:
            return 2

    def func_1(self):
        error_type, error_info = function.catch_error(self.r.text)
        if ADAPTION_FLAG:
            error_info_str = ''.join(error_info)
            mutate = ErrorModeling.ErrorModeling(error_info_str, '1', self.modeling_data[self.index], TE_NAME)
            new_modeling, new_seed = mutate.generate_seed()
            if new_seed:
                self.mutate_all += 1
                try:
                    r = requests.get(url=function.get_te_url(TE_NAME), params=
                    {
                        'a': parse.quote(new_modeling + new_seed),
                        "filename": "seed1.txt"
                    }, timeout=3)
                except BaseException as e:
                    logger.info("Web System Error")
                    logger.info(e)
                    return 0
                if "xdebug-error" in r.text:
                    error_type, error_info = function.catch_error(r.text)
                    self.error_type_list.append(error_type)
                    self.modeling_list.append(new_modeling + new_seed)
                    self.error_info_list.append(error_info)
                else:
                    self.mutate_success += 1
                    self.normal_list.append(new_modeling + new_seed)
                    self.error_type_list.append(error_type)
                    self.modeling_list.append(self.modeling_data[self.index])
                    self.error_info_list.append(error_info)
        return 1

    def save(self):
        df2 = pd.DataFrame({
            "modeling": self.normal_list
        })
        logger.info("[*]Seed check completed")
        df2.to_excel(SEED_LOG_PATH + TE_NAME + "normal_R1.xlsx", index=False)

    def check_2(self):
        self.get_seed_data()
        for i in tqdm.tqdm(range(0, len(self.modeling_data))):
            self.index = i
            try:
                r = requests.get(url=function.get_te_url(TE_NAME),
                                 params={'a': parse.quote(self.modeling_data[i]),
                                         "filename": "seed1.txt"}, timeout=3)
                function.clean_te_cache(TE_NAME)
                self.r = r
            except BaseException as e:
                logger.info("Web System Error")
                logger.info(e)
                continue
            if "xdebug-error" in r.text:
                error_type, error_info = function.catch_error(r.text)
                if error_type.__len__() == 1 and error_type[0] == 'Warning':
                    continue
                logger.info(self.modeling_data[i])
