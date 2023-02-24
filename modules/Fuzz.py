import function
from urllib import parse
from logger import logger
import pandas as pd
import requests
import tqdm
from modules import ErrorModeling, Input
from config import *


class Fuzz():

    def __init__(self) -> None:
        logger.info("[*]start fuzzing")
        self.sink_file_name = ''
        self.test_case_num = 0
        self.final_res_all = 0
        self.mutate_still_error = []
        self.mutate_still_error_info = []
        self.mutate_num = 0
        self.mutate_still_te_error_num = 0
        self.normal = 0
        self.char = ''
        self.parse_error = 0
        self.other_error = 0
        self.index = 0
        self.poc_res = []
        self.poc_char = []
        self.poc_location = []
        self.poc_controllable_line = []
        self.r = None
        self.repeat_flag = 0
        self.modeling_location = 0
        self.payload = None
        self.error_info = None
        self.error_type = None
        self.tag_modeling = []
        self.controllable_line = []
        self.sink = []

    def set_sink_file_name(self, filename):
        self.sink_file_name = filename

    def get_sink_data(self):
        self.tag_modeling, self.sink, self.controllable_line = function.get_fuzz_info_from_excel(self.sink_file_name)

    def fuzz(self):
        fuzz_char = Input.Input().get_fuzz_char_1() + Input.Input().get_close_char()
        self.get_sink_data()
        for i in tqdm.tqdm(range(0, len(self.tag_modeling))):
            function.clean_te_cache(TE_NAME)
            self.index = i
            for fuzz_c in fuzz_char:
                self.char = fuzz_c
                str_list = list(self.tag_modeling[i])
                str_list.insert(self.sink[i], fuzz_c)
                payload = ''.join(str_list)
                self.payload = payload
                self.test_case_num = self.test_case_num + 1
                try:
                    r = requests.get(url=function.get_te_url(TE_NAME),
                                     params={'a': payload,
                                             "filename": "fuzz.txt"}, timeout=3)
                    self.r = r
                except BaseException as e:
                    logger.info("Web System Error")
                    logger.info(e)
                    continue
                status_code = self.content_analysis()
                if status_code == 0:
                    self.save_poc()
                    break
                elif status_code == 1:
                    if ADAPTION_FLAG:
                        error_info_str = ''.join(self.error_info)
                        mutate = ErrorModeling.ErrorModeling(error_info_str, fuzz_c, payload, TE_NAME)
                        new_modeling, new_seed = mutate.generate_seed()
                        if new_seed:
                            self.mutate_num = self.mutate_num + 1
                            str_list = list(new_modeling)
                            newpayload = ''.join(str_list)
                            self.payload = newpayload
                            try:
                                r = requests.get(url=function.get_te_url(TE_NAME),
                                                 params={'a': newpayload,
                                                         "filename": "fuzz.txt"}, timeout=3)
                                self.r = r
                            except BaseException as e:
                                logger.info("Web System Error")
                                logger.info(e)
                            status_code = self.content_analysis()
                            if status_code == 0:
                                self.save_poc()
                                break
                            elif status_code == 1:
                                self.mutate_still_error.append(parse.quote(newpayload))
                                self.mutate_still_error_info.append(parse.quote(error_info_str))
                                self.mutate_still_te_error_num += 1
                            else:
                                self.normal += 1

        self.save()

    def content_analysis(self):
        if "xdebug-error" in self.r.text:
            self.error_type, self.error_info = function.catch_error(self.r.text)
            if 'Parse error' in self.error_type or "Uncaught ParseError" in self.error_type:
                return 0
            else:
                return 1
        else:
            return 2

    def save_poc(self):
        self.poc_char.append(parse.quote(self.char))
        self.poc_res.append(parse.quote(self.payload))
        self.poc_location.append(self.sink[self.index])
        self.poc_controllable_line.append(self.controllable_line[self.index])
        self.parse_error += 1

    def save(self):
        logger.info("test_case_num :" + str(self.test_case_num))
        logger.info("parse_error :" + str(self.parse_error))
        df = pd.DataFrame(
            {
                "poc": self.poc_res,
                "poc_location": self.poc_location,
                "controllable_line": self.poc_controllable_line,
                "fuzz_char": self.poc_char
            })
        df.to_excel(POC_PATH + TE_NAME + "_poc.xlsx", index=False)


