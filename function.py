import re
import pandas as pd
import os
import shutil
import requests
from urllib import parse
from config import *
from logger import logger


def get_file_name_from_directory(file_dir):
    """
    use in seed collect step
    get document and testcase from source code

    :param file_dir: file directory
    :returns: filename  list in target directory
    """
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file):
                L.append(os.path.join(root, file))
    return L


def catch_error(html_content):
    """
    catch any type error message
    :param: html_content: http request response content
    :return: error type and error message
    """
    html_content = html_content.replace("<i>", "").replace("</i>", "")
    reg_rule = '\( ! \)<\/span>([\s\S]*?)<\/th>'
    res = re.findall(reg_rule, html_content)
    error_type = []
    error_info = []
    for i in res:
        error_type.append(i.split(':', 1)[0].strip())
        error_info.append(i.split(':', 1)[1].strip())
    return error_type, error_info


def catch_code_coverage_and_filename(response):
    """
    :param response: http request response
    :return: (code coverage,cache fileanme)
    """
    try:
        return response.headers['Code-Coverage'], response.headers['Cache-File']
    except:
        return '0', '0'


def read_data_from_excel(filename, row):
    """
    :param filename:
    :param row:
    :return: excel data
    """
    res = []
    df = pd.read_excel(filename, names=None)
    df_list = df.values.tolist()
    for s_li in df_list:
        res.append(s_li[row])
    return res


def generate_new_file(path, new_filename):
    """
    :param path:
    :param new_filename:
    :return:
    """
    if '/' in new_filename:
        dir_list = new_filename.split('/')
        for i in range(0, len(dir_list)):
            try:
                if not os.path.exists(path + "/".join(dir_list[0:i])):
                    os.mkdir(path + "/".join(dir_list[0:i]))
            except:
                continue
    try:
        open(path + new_filename, 'a').close()
    except:
        pass



def get_te_url(te_name):
    if te_name == "smarty":
        return "http://"+TARGET_IP+"/smarty/demo/index.php?a="
    elif te_name == "twig":
        return "http://"+TARGET_IP+"/twig/?a="
    elif te_name == "dwoo":
        return "http://"+TARGET_IP+"/dwoo/index.php?a="
    elif te_name == "mustache":
        return "http://"+TARGET_IP+"/mustache/?a="
    elif te_name == "latte":
        return "http://"+TARGET_IP+"/latte/?a="
    elif te_name == "fenom":
        return "http://"+TARGET_IP+"/fenom/?a="
    elif te_name == "thinkphp":
        return "http://"+TARGET_IP+"/thinkphp/?a="
    return "Bad te name!"


def get_te_mutate_path(te_name):
    if te_name == "smarty":
        return BASE_TE_PATH+"smarty/demo/"


def get_te_cache_path(te_name):
    if te_name == "smarty":
        return BASE_TE_PATH + "smarty/demo/templates_c/"
    elif te_name == "twig":
        return BASE_TE_PATH + "twig/"
    elif te_name == "dwoo":
        return BASE_TE_PATH + "dwoo/lib/compiled/*"
    elif te_name == "mustache":
        return BASE_TE_PATH + "mustache/"
    elif te_name == "latte":
        return BASE_TE_PATH + "latte/"
    elif te_name == "fenom":
        return BASE_TE_PATH + "fenom/template/"
    elif te_name == "thinkphp":
        return BASE_TE_PATH + "thinkphp/"
    else:
        return None


def clean_te_cache(te_name):
    if te_name == "smarty":
        os.system("rm -rf " + BASE_TE_PATH + "smarty/demo/templates_c/*")
        os.system("rm -rf " + BASE_TE_PATH + "smarty/demo/cache/*")
    elif te_name == "twig":
        os.system("rm -rf " + BASE_TE_PATH + "twig/cache/*")
    elif te_name == "dwoo":
        os.system("rm -rf " + BASE_TE_PATH + "dwoo/lib/compiled/*")
        os.system("rm -rf " + BASE_TE_PATH + "dwoo/test/*")
    elif te_name == "mustache":
        os.system("rm -rf " + BASE_TE_PATH + "mustache/cache/*")
    elif te_name == "latte":
        os.system("rm -rf " + BASE_TE_PATH + "latte/tempdir/*")
        os.system("rm -rf " + BASE_TE_PATH + "latte/template/*")
    elif te_name == "fenom":
        os.system("rm -rf " + BASE_TE_PATH + "fenom/template/*")
        # os.system("rm -rf " + BASE_TE_PATH + "fenom/templates/*")
    elif te_name == "thinkphp":
        os.system("rm " + BASE_TE_PATH + "thinkphp/runtime/*")
        os.system("rm -rf " + BASE_TE_PATH + "thinkphp/runtime/*")
    else:
        return None


def get_controllable_line(te_name, file_name):
    if BASE_TE_PATH not in file_name:
        file_name = get_te_cache_path(te_name) + file_name
    else:
        file_name = file_name
    res = []
    try:
        content = open(file_name, 'r', encoding='utf-8').readlines()
        for i in range(0, len(content)):
            if UNIQUE_STRING in content[i]:
                res.append(i + 1)
        return res
    except BaseException as e:
        logger.info("read file " + file_name + " error")
        logger.info(e)
    return [-1]


def execute_func(te_name, modeling_string, cc_file):
    try:
        r = requests.get(url=get_te_url(te_name),
                         params={'a': parse.quote(modeling_string),
                                 "filename": cc_file}, timeout=3)
        clean_te_cache(te_name)
        return r
    except BaseException as e:
        logger.info(e)
        return None


def get_fuzz_info_from_excel(filename):
    data = pd.read_excel(SINK_PATH + filename, sheet_name="Sheet1")
    data = data.values.tolist()
    tag_modeling = []
    sink = []
    controllable_line = []
    for d in data:
        tag_modeling.append(d[0])
        sink.append(d[1])
        controllable_line.append(d[3])
    return tag_modeling, sink, controllable_line
