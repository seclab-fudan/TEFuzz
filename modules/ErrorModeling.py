# coding:utf-8
# Author:altman
import re
import os
import function
import config




class ErrorModeling():
    def __init__(self, error_message, seed, modeling, te_name) -> None:
        self.error_message = error_message
        self.seed = seed
        self.te_name = te_name
        self.modeling = modeling

    """
    """

    def smarty_mutate(self):
        if re.findall("Unable to load config '(.*?)'", self.error_message):
            filename = re.findall("Unable to load config '(.*?)'", self.error_message)[0].split(":")[-1]
            function.generate_new_file(function.get_te_mutate_path(self.te_name), filename)
            return self.modeling, self.seed

        if re.findall("Unable to load template '(.*?)'", self.error_message):
            filename = re.findall("Unable to load template '(.*?)'", self.error_message)[0].split(":")[-1]
            # self.modeling = self.modeling.replace(filename, "template/test.tpl")
            function.generate_new_file(function.get_te_mutate_path(self.te_name), filename)
            return self.modeling, self.seed

        if re.findall("Unable to load file '(.*?)'", self.error_message):
            filename = re.findall("Unable to load file '(.*?)'", self.error_message)[0].split(":")[-1]
            function.generate_new_file(function.get_te_mutate_path(self.te_name), filename)
            return self.modeling, self.seed

        if re.findall("cannot read resource '(.*?)'", self.error_message):
            filename = re.findall("cannot read resource '(.*?)'", self.error_message)[0].split(":")[-1]
            function.generate_new_file(function.get_te_mutate_path(self.te_name), filename)
            return self.modeling, self.seed

        if re.findall("not trusted file path '(.*?)'", self.error_message):
            filename = re.findall("not trusted file path '(.*?)'", self.error_message)[0].split(":")[-1]
            modeling_file_name = filename.replace(config.BASE_TE_PATH+"smarty/demo/", "")
            filename = filename.replace('smarty/demo/', 'smarty/demo/templates/')
            function.generate_new_file("", filename)
            return self.modeling.replace(modeling_file_name, "templates/" + modeling_file_name), self.seed

        if re.findall("URI '(.*?)' not allowed by security setting", self.error_message):
            filename = re.findall("URI '(.*?)' not allowed by security setting", self.error_message)[0].split(":")[-1]
            self.modeling = self.modeling.replace(filename, "template/test.tpl")
            os.chmod(function.get_te_mutate_path(self.te_name) + "template/test.tpl")
            return self.modeling, self.seed


        if re.findall("Not matching ({.*?})({/.*?})", self.error_message):
            add_string = re.findall("Not matching ({.*?})({\/.*?})", self.error_message)[1][1]
            self.modeling = self.modeling + add_string
            return self.modeling, self.seed

        if re.findall("missing '(.*?)' parameter", self.error_message):
            return self.modeling.replace("aLtMan", ""), self.seed

        if re.findall("missing '(.*?)' attribute", self.error_message):
            return self.modeling.replace("aLtMan", ""), self.seed

        if re.findall("unclosed {(.*?)}", self.error_message):
            self.modeling = self.modeling + "{/" + re.findall("unclosed {(.*?)}", self.error_message)[0] + "}"
            return self.modeling, self.seed

        if re.findall("illegal value", self.error_message):
            return self.modeling, self.seed

        if re.findall("'([\s\S]*?)' is not a valid image file", self.error_message):
            return self.modeling, self.seed

        return self.modeling, None


    def twig_mutate(self):
        if re.findall("Unable to find template \"([\s\S]*?)\"", self.error_message):
            filename = re.findall("Unable to find template \"([\s\S]*?)\"", self.error_message)[0]
            function.generate_new_file(config.BASE_TE_PATH+'/twig/templates/', filename)
            return self.modeling, self.seed
        if re.findall("Unexpected \"}\"", self.error_message):
            return self.modeling, self.seed + "{"

        if re.findall("expecting closing tag for the \"([\s\S]*?)\" tag", self.error_message):
            tag_name = "end" + re.findall("expecting closing tag for the \"([\s\S]*?)\" tag", self.error_message)[0]
            return self.modeling + "{% " + tag_name + " %}", self.seed

        if re.findall("Unclosed \"\"\"", self.error_message):
            return self.modeling, self.seed + "\""

        if re.findall("Unclosed \"\(\" ", self.error_message):
            return self.modeling, self.seed + ")"

        if re.findall("end of print statement", self.error_message):
            return self.modeling, self.seed + "}}"

        if re.findall("expecting closing tag for the \"(.*?)\" tag", self.error_message):
            end_tag = re.findall("expecting closing tag for the \"(.*?)\" tag", self.error_message)[0]
            return self.modeling + "{% " + end_tag + " %}", self.seed

        return self.modeling, None


    def dwoo_mutate(self):
        if re.findall("Resource \"([\s\S]*?)\" not found", self.error_message):
            filename = re.findall("Resource \"file:([\s\S]*?)\" not found", self.error_message)[0].split(":")[-1]
            function.generate_new_file(config.BASE_TE_PATH+'dwoo/', filename)
            return self.modeling, self.seed

        if re.findall("Unfinished string", self.error_message):
            return self.modeling, self.seed + "\""

        return self.modeling, None


    def mustache_mutate(self):
        if re.findall(" Missing closing tag: ([\s\S]*?) opened", self.error_message):
            tag_name = re.findall(" Missing closing tag: ([\s\S]*?) opened", self.error_message)[0]
            closing_tag = "{{/ " + tag_name + " }}"
            return self.modeling + closing_tag, self.seed

        if re.findall("Nesting error: ([\s\S]*?) \(on line 0\) vs. ([\s\S]*?) \(on line 0\)", self.error_message):
            tag_name1 = \
                re.findall("Nesting error: ([\s\S]*?) \(on line 0\) vs. ([\s\S]*?) \(on line ", self.error_message)[0][
                    0]
            tag_name2 = \
                re.findall("Nesting error: ([\s\S]*?) \(on line 0\) vs. ([\s\S]*?) \(on line ", self.error_message)[0][
                    1]
            return self.modeling.replace("{/ " + tag_name2 + " }", "{/ " + tag_name1 + " }"), self.seed
        return self.modeling, None


    def latte_mutate(self):
        if re.findall("Missing template file 'template/([\s\S]*?)'", self.error_message):
            filename = re.findall("Missing template file 'template/([\s\S]*?)'", self.error_message)[0]
            function.generate_new_file(config.BASE_TE_PATH+'latte/template/', filename)
            return self.modeling, self.seed

        if re.findall("Missing ([\s\S]*?) in", self.error_message):
            tag_name = re.findall("Missing ([\s\S]*?) in", self.error_message)[0]
            return self.modeling + tag_name, self.seed

        if re.findall("Tag {([\s\S]*?)} must be inside", self.error_message):
            return self.modeling, self.seed

        if re.findall("Tag {([\s\S]*?)} is unexpected here", self.error_message):
            tag_name = re.findall("Tag ({[\s\S]*?}) is unexpected here", self.error_message)[0]
            return self.modeling.replace(tag_name, ""), self.seed

        if re.findall("Cannot include undefined parent block '([\s\S]*?)'", self.error_message):
            block_name = re.findall("Cannot include undefined parent block '([\s\S]*?)'", self.error_message)
            return self.modeling.replace(block_name,""), self.seed

        if re.findall("should be '([\s\S]*?)' replaced with '([\s\S]*?)'",self.error_message):
            value = re.findall("should be '([\s\S]*?)' replaced with '([\s\S]*?)'", self.error_message)
            return self.modeling.replace(value[0][0], value[0][1]), self.seed
        return self.modeling, None


    def fenom_mutate(self):
        if re.findall("Template ([\s\S]*?) not found", self.error_message):
            filename = re.findall("Template ([\s\S]*?) not found", self.error_message)[0]
            function.generate_new_file(config.BASE_TE_PATH+'fenom/templates/', filename)
            return self.modeling, self.seed

        if re.findall("Unclosed tag in line", self.error_message):
            return self.modeling + "}", self.seed

        if re.findall("Unclosed comment block in line", self.error_message):
            return self.modeling + "*}", self.seed

        if re.findall("Unexpected closing of the tag '([\s\S]*?)'", self.error_message):
            tag_name = re.findall("Unexpected closing of the tag '([\s\S]*?)'", self.error_message)[0]
            return self.modeling.replace("{/" + tag_name + "}", ""), self.seed

        return self.modeling, None

    def rain3_mutate(self):
        if re.findall("Template ([\s\S]*?) not found", self.error_message):
            template_name = re.findall("Template ([\s\S]*?) not found", self.error_message)[0] + ".html"
            function.generate_new_file('', template_name)
            return self.modeling, self.seed

        if re.findall("You need to close an {([\s\S]*?)} tag", self.error_message):
            tag_name = re.findall("You need to close an {([\s\S]*?)} tag", self.error_message)[0]
            return self.modeling + "{/" + tag_name + "}", self.seed

        if re.findall("Class '([\s\S]*?)' not found", self.error_message):
            classname = re.findall("Class '([\s\S]*?)' not found", self.error_message)[0]
            return self.modeling, self.seed

        return self.modeling, None

    def elefant_mutate(self):
        return self.modeling, None


    def thinkphp_mutate(self):
        if re.findall("template not exists:([\s\S]*?) in", self.error_message):
            template_name = re.findall("template not exists:([\s\S]*?) in", self.error_message)[0]
            function.generate_new_file(config.BASE_TE_PATH+"thinkphp/", template_name)
            return self.modeling, self.seed
        if re.findall("Call to undefined function ([\s\S]*?) in", self.error_message):
            return self.modeling, self.seed
        if re.findall("Class ([\s\S]*?) not found", self.error_message):
            return self.modeling, self.seed
        if re.findall("Class name must be a valid object or a string", self.error_message):
            return self.modeling, self.seed
        return self.modeling, None

    def generate_seed(self):
        return eval("self." + self.te_name + "_mutate")()



