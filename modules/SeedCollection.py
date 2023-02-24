import requests
import re
import pandas as pd
import tqdm
from config import SEED_LOG_PATH
from bs4 import BeautifulSoup
import os
import function
import json


class SeedCollection():
    def __init__(self) -> None:
        pass

    @staticmethod
    def smarty_crawler():
        print("[*]Smarty")
        SMARTY_URL = "https://www.smarty.net/docs/en/"
        r = requests.get(SMARTY_URL)
        link_re = '<a href="(.*?)">'
        link = re.findall(link_re, r.text)
        for i in range(0, len(link)):
            if "http" in link[i] or "/" in link[i]:
                link[i] = ''
        link = set(link)
        link = list(link)
        te_modeling = []
        s = requests.session()
        s.keep_alive = False
        for i in tqdm.tqdm(link):
            with s.get(SMARTY_URL + i) as r:
                html_content = re.findall("<pre class=\"programlisting\">([\s\S]*?)<\/pre>", r.text)
                if html_content.__len__() == 0:
                    continue
            te_re1 = "({([a-z].*?).*?}[\s\S]*?{/\\2})"
            te_modeling.extend(re.findall(te_re1, html_content[0]))
            html_content = re.sub(te_re1, "", html_content[0])
            te_re = "({.*?})"
            te_modeling.extend(re.findall(te_re, html_content))
            te_modeling = set(te_modeling)
            te_modeling = list(te_modeling)
        print(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "smarty.xlsx", index=False)
        print("[*]Finished")

    @staticmethod
    def twig_crawler():
        TWIG_URL = "https://twig.symfony.com"
        r = requests.get(TWIG_URL + "/doc/3.x/")
        link_re = '<a href="(.*?)">'
        link = re.findall(link_re, r.text)
        for i in range(0, len(link)):
            if "http" in link[i]:
                link[i] = ''
        link = set(link)
        link = list(link)
        te_modeling = []
        for i in tqdm.tqdm(link):
            print(TWIG_URL + i)
            code_content = ''
            r = requests.get(TWIG_URL + i)
            soup = BeautifulSoup(r.text, 'html.parser')
            code = soup.find_all('code')
            for x in code:
                code_content = code_content + x.text
            te_re1 = "({% ([a-z]*?).*? %}[\s\S]*?{% end\\2 %})"
            te_re2 = "({% [\s\S]*? %})"
            te_re3 = "({{.*?}})"
            re_1_res = re.findall(te_re1, code_content)
            for n in re_1_res:
                te_modeling.append(n[0])
            code_content = re.sub(te_re1, "", code_content)
            te_modeling.extend(re.findall(te_re2, code_content))
            code_content = re.sub(te_re2, "", code_content)
            te_modeling.extend(re.findall(te_re3, code_content))
            te_modeling = set(te_modeling)
            te_modeling = list(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "twig.xlsx", index=False)

    @staticmethod
    def latte_crawler():
        LATTE_URL = "https://latte.nette.org/"
        r = requests.get(LATTE_URL + "en/guide")
        link_re = '<a href="(.*?)">'
        link = re.findall(link_re, r.text)
        te_modeling = []
        for i in range(0, len(link)):
            if "https" not in link[i] or "latte" not in link[i]:
                link[i] = ''
        link = set(link)
        link = list(link)
        s = requests.session()
        s.keep_alive = False
        for i in tqdm.tqdm(link[1:]):
            try:
                r = s.get(i, timeout=5)
            except:
                print(i + "  服务器错误")
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            code = soup.find_all('code')
            te_re1 = "({([a-z]*?).*?}[\s\S]*?{\/\\2})"
            te_re2 = "({.*?})"
            for x in code:
                code_content = x.text
                print(x.text)
                print("*" * 50)
                re_1_res = re.findall(te_re1, code_content)
                for n in re_1_res:
                    te_modeling.append(n[0])
                code_content = re.sub(te_re1, "", code_content)
                te_modeling.extend(re.findall(te_re2, code_content))
            te_modeling = set(te_modeling)
            te_modeling = list(te_modeling)
            df = pd.DataFrame({"modeling": te_modeling})
            df.to_excel(SEED_LOG_PATH + "latte.xlsx", index=False)

    @staticmethod
    def dwoo_crawler():
        te_modeling = []
        DWOO_DIR = "Dwoo-1.1.1/tests/"
        file_list = function.get_file_name_from_directory(DWOO_DIR)
        re1 = "'({.*?})'"
        re2 = "({([a-z]*?) .*?}[\s\S]*?{(\/\\2)})"
        for file in file_list:
            if os.path.splitext(file)[-1] == '.php':
                data = open(file, "r").read()
                te_modeling.extend(re.findall(re1, data))
            if os.path.splitext(file)[-1] == '.html':
                data = open(file, "r").read()
                te_modeling.extend([n[0] for n in re.findall(re2, data)])
                data = re.sub(re2, "", data)
                te_modeling.extend(re.findall(re1, data))
        te_modeling = set(te_modeling)
        te_modeling = list(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "dwoo.xlsx", index=False)

    @staticmethod
    def fenom_crawler():
        te_modeling = []
        FENOM_DIR = "/Users/altm4nz/site/ssti/fenom/vendor/fenom/fenom/docs/en/"
        file_list = function.get_file_name_from_directory(FENOM_DIR)
        re0 = "```smarty\n([\s\S]*?)\n```"
        re1 = "({([a-z]*?).*?}[\s\S]*?{/\\2})"
        re2 = "({.*?})"
        for file in file_list:
            data = open(file, "r").read()
            tmp_codes = re.findall(re0, data)
            for tmp_code in tmp_codes:
                te_modeling.extend([n[0] for n in re.findall(re1, tmp_code)])
                tmp_code2 = re.sub(re1, "", tmp_code)
                te_modeling.extend(re.findall(re2, tmp_code2))
        te_modeling = set(te_modeling)
        te_modeling = list(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "fenom.xlsx", index=False)

    @staticmethod
    def rain3_crawler():
        te_modeling = []
        DOC_URL = "https://github.com/feulf/raintpl3/wiki/Documentation-for-web-designers"
        RAIN_DIR = "raintpl3-master/templates"
        file_list = function.get_file_name_from_directory(RAIN_DIR)
        re1 = "({([a-z]*?).*?}[\s\S]*?{/\\2})"
        re2 = "({.*?})"
        for file in file_list:
            if os.path.splitext(file)[-1] == '.html':
                data = open(file, "r").read()
                te_modeling.extend([n[0] for n in re.findall(re1, data)])
                tmp_data = re.sub(re1, "", data)
                te_modeling.extend(re.findall(re2, tmp_data))
        r = requests.get(DOC_URL)
        html_content = re.sub("(<script>[\s\S]*?</script>)", "", r.text)
        te_modeling.extend([n[0] for n in re.findall(re1, html_content)])
        tmp_data = re.sub(re1, "", data)
        te_modeling.extend(re.findall(re2, tmp_data))
        te_modeling = set(te_modeling)
        te_modeling = list(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "rain3.xlsx", index=False)

    @staticmethod
    def elefant_crawler():
        te_modeling = []
        DIR = "elefant/"
        file_list = function.get_file_name_from_directory(DIR)
        html_file_list = [file for file in file_list if os.path.splitext(file)[-1] == '.html']
        re1 = "{%.*?%}[\s\S]*?{% end %}"
        re2 = "{{[\s\S]*?}}"
        for file in html_file_list:
            tmp_res = elefant_collect(file)
            data = open(file, "r").read()
            te_modeling.extend(tmp_res)
            for n in tmp_res:
                data = data.replace(n, "")
            te_modeling.extend(re.findall(re2, data))
        te_modeling = set(te_modeling)
        te_modeling = list(te_modeling)
        print(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "elefant.xlsx", index=False)

    @staticmethod
    def elefant_collect(filename):
        check = 0
        flag = 0
        re1 = "({%.*?%})"
        startline = -1
        endline = -1
        res = []
        lines = open(filename, "r").readlines()
        for linenum in range(0, len(lines)):
            tag = (re.findall(re1, lines[linenum]))
            for i in tag:
                if i == "{% else %}":
                    continue
                if i != "{% end %}" and check == 0:
                    startline = linenum
                    check = 1
                    flag += 1
                elif i != "{% end %}" and check == 1:
                    flag += 1
                if i == "{% end %}":
                    flag -= 1
                    if flag == 0:
                        endline = linenum
                if startline != -1 and endline != -1:
                    res.append("".join(lines[startline:endline + 1]))
                    startline = -1
                    endline = -1
                    check = 0
        return res

    @staticmethod
    def thinkphp_crawler():
        THINK_URL = "https://www.kancloud.cn/manual/think-template/"
        r = requests.get(THINK_URL + "1286403")
        link_re = '<a href="(.*?)">'
        link = re.findall(link_re, r.text)
        te_modeling = []
        link = set(link)
        link = list(link)
        for i in tqdm.tqdm(link):
            r = requests.get(THINK_URL + i)
            content_data = re.findall('\"article\":([\s\S]*?),\n        \"summary\"', r.text)
            content_data = json.loads(content_data[0])
            html_content = content_data['content']
            code_list = re.findall("~~~([\s\S]*?)~~~", html_content)
            for code in code_list:
                re1 = "({([a-z].*?).*?}[\s\S]*?{/\\2})"
                re2 = "({.*?})"
                re1_res = re.findall(re1, code)
                if len(re1_res) > 0:
                    te_modeling.extend([n[0] for n in re1_res])
                    code = re.sub(re1, "", code)
                te_modeling.extend(re.findall(re2, code))
            te_modeling = set(te_modeling)
            te_modeling = list(te_modeling)
        df = pd.DataFrame({"modeling": te_modeling})
        df.to_excel(SEED_LOG_PATH + "thinkphp.xlsx", index=False)
