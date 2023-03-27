from config import TE_NAME
from modules import  SinkDetect, Fuzz, Exploit
from Logger import logger

if __name__ == "__main__":
    logger.info("[*]Target TE : " + TE_NAME)
    sink_detect= SinkDetect.SinkDetect()
    sink_detect.set_seed_file_name(TE_NAME + "_test.xlsx")
    sink_detect.detect()
    fuzz = Fuzz.Fuzz()
    fuzz.set_sink_file_name(TE_NAME+"_sink.xlsx")
    fuzz.fuzz()
    exp = Exploit.Exploit()
    exp.set_poc_file_name(TE_NAME+"_poc.xlsx")
    exp_list = exp.code_wrapper()
    logger.info("[*]Generate "+str(exp_list.__len__())+" EXP")
    logger.info(exp_list)
    if exp_list:
        logger.info("[*]Check success!")
