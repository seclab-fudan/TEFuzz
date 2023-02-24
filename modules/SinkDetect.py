import function
from logger import logger
import pandas as pd
import requests
import tqdm
from modules import ErrorModeling
from config import *


class SinkDetect():
    test_case_num = 0
    final_res_all = 0
    final_res = []
    mutate_num = 0
    poc_location = []
    poc_line = []
    mutate_still_error = []
    mutate_still_error_info = []
    mutate_still_te_error_num = 0
    seed_file_name = ''
    index = 0
    poc_res = []
    modeling_data = None
    r = None
    repeat_flag = 0
    modeling_location = 0
    payload = None
    error_info = None
    error_type = None

    def __init__(self) -> None:
        logger.info("[*]Sink detect start")
        pass

    def set_seed_file_name(self, filename):
        self.seed_file_name = filename

    def get_seed_data(self):
        self.modeling_data = function.read_data_from_excel(SEED_LOG_PATH + self.seed_file_name, 0)

    def detect(self):
        self.get_seed_data()
        for i in tqdm.tqdm(self.modeling_data):
            modeling_len = i.__len__()
            self.index = i
            for modeling_location in range(1, modeling_len):
                self.modeling_location = modeling_location
                self.test_case_num = self.test_case_num + 1
                function.clean_te_cache(TE_NAME)
                str_list = list(i)
                str_list.insert(modeling_location, UNIQUE_STRING)
                self.payload = ''.join(str_list)
                try:
                    r = requests.get(url=function.get_te_url(TE_NAME),
                                     params={'a': self.payload,
                                             "filename": "sink.txt"}, timeout=3)
                    self.r = r
                except BaseException as e:
                    logger.info("Web System Error")
                    logger.info(e)
                    continue
                status_code = self.content_analysis()
                if status_code == 0:
                    self.func_0()
                elif status_code == 1:
                    self.func_1()
                elif status_code == 2:
                    self.func_1()
                elif status_code == 3 and ADAPTION_FLAG:
                    self.func_3()
        logger.info("testcase_num :" + str(self.test_case_num))
        logger.info("interesting_testcase_num:" + str(self.final_res_all))
        logger.info("unique_testcase_num :" + str(self.final_res.__len__()))
        self.save()

    def func_0(self):
        self.poc_res.append(self.payload)
        self.poc_location.append(self.modeling_location)
        cc, cachefile = function.catch_code_coverage_and_filename(self.r)
        controllable_line = function.get_controllable_line(TE_NAME, cachefile)
        self.poc_line.append(controllable_line)

    def func_1(self):
        self.final_res_all = self.final_res_all + 1
        cc, cachefile = function.catch_code_coverage_and_filename(self.r)
        if cachefile == '0':
            logger.info(self.payload)
        controllable_line = function.get_controllable_line(TE_NAME, cachefile)
        self.reset_flag()
        for tmp_i in range(0, len(self.final_res)):
            if self.final_res[tmp_i][0] == self.index and self.final_res[tmp_i][2] == cc and self.final_res[tmp_i][
                3] == controllable_line:
                self.repeat_flag = 1
        if not self.repeat_flag and controllable_line.__len__() != 0:
            self.final_res.append([self.index, self.modeling_location, cc, controllable_line])

    def func_3(self):
        error_info_str = ''.join(self.error_info)
        mutate = ErrorModeling.ErrorModeling(error_info_str, UNIQUE_STRING, self.payload, TE_NAME)
        new_modeling, new_seed = mutate.generate_seed()
        if new_seed:
            self.mutate_num = self.mutate_num + 1
            str_list = list(new_modeling)
            new_payload = ''.join(str_list)
            try:
                r = requests.get(url=function.get_te_url(TE_NAME),
                                 params={'a': new_payload,
                                         "filename": "sink.txt"}, timeout=3)
                self.r = r
            except BaseException as e:
                logger.info("Web System Error")
                logger.info(e)
            status_code = self.content_analysis()
            if status_code == 0:
                self.func_0()
            elif status_code == 1 or status_code == 3:
                self.mutate_still_error.append(new_payload)
                self.mutate_still_error_info.append(error_info_str)
                self.mutate_still_te_error_num += 1
            else:
                self.func_1()

    def save(self):
        if ADAPTION_FLAG:
            df = pd.DataFrame({"modeling": self.mutate_still_error, "error message": self.mutate_still_error_info})
            df.to_excel(SINK_PATH + TE_NAME + "_te_error.xlsx", index=False)
        modeling = []
        location = []
        cc = []
        controllable_line = []
        for i in self.final_res:
            modeling.append(i[0])
            location.append(i[1])
            cc.append(i[2])
            controllable_line.append(i[3])
        logger.info("[*]Sink detect completed")
        df = pd.DataFrame(
            {"modeling": modeling, "location": location, "cc": cc, "controllable_line": controllable_line}
        )
        df.to_excel(SINK_PATH + TE_NAME + "_sink.xlsx", index=False)
        if self.poc_res.__len__() > 0:
            df = pd.DataFrame(
                {
                    "poc": self.poc_res,
                    "poc_location": self.poc_location,
                    "controllable_line": self.poc_line,
                    "fuzz_char": UNIQUE_STRING
                })
            df.to_excel(POC_PATH + TE_NAME + "_sink_poc.xlsx", index=False)

    def reset_flag(self):
        self.repeat_flag = 0

    def content_analysis(self):
        if "xdebug-error" in self.r.text:
            self.error_type, self.error_info = function.catch_error(self.r.text)
            if 'Parse error' in self.error_type:
                return 0,
            elif 'Notice' in self.error_type:
                return 1
            else:
                return 3
        else:
            return 2
