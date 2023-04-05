# TEFuzz 
This repository provides the tool for the paper "Remote Code Execution from SSTI in the Sandbox: Automatically Detecting and Exploiting Template Escape Bugs" accepted at USENIX Security '23.

Table of Contents
=================
* [Requirements](#requirements)
* [Structure](#Structure)
* [Getting Started Instructions](##getting-started-instructions)
* [Publication](##publication)

## Requirements

* OS: 
  - TEFuzz is developed and tested under Ubuntu 18.04.
* Python3 (>= 3.8)
* PHP7.2 && Composer
* Docker 

## Structure

* TEFuzz
  * CodeWrapper: context-sensitive code wrapping based on php-parser.
  * modules: 
    * ErrorModeling.py: script for modeling error messages. 
    * SeedCheck.py && SeedCheck.py: script for init seeds.
    * SinkDetect.py: script for identifying interesting testcase.
    * Fuzz.py: script for generating PoCs.
    * Exploit.py: script for generating EXPs.
  * check.py: script for basic testing.
  * main.py: Run entry of TEFuzz.
* TE driver: Template engine running environment.

## Getting Started Instructions
### **0. Clone the TEFuzz repository**

```bash
git clone https://github.com/seclab-fudan/TEFuzz
```

### **1. Install dependencies of TEFuzz**

```bash
sudo apt-get update
sudo apt-get install python3.8 python3-pip
python3.8 -m pip install -r requirements.txt
cd $YOUR_TEFUZZ_PATH/CodeWrapper && composer install
```
### **2. Build docker of TE driver**
#### docker image
For convenience, we provide a docker image for the Target TE running environment.
You need to mount docker's `/var/www/html/tefuzz` directory to the host so that tools can read the information.

```bash
docker pull altm4nz/tefuzz:1.0
docker run -itd -p 80:80 -v /var/www/html/tefuzz:/var/www/html/tefuzz --name tefuzz altm4nz/tefuzz:1.0 
docker cp tefuzz:/tmp/tefuzz/ /var/www/html/
docker cp tefuzz:/tmp/seed/ $YOUR_TEFUZZ_PATH/result/
docker exec -it tefuzz /bin/bash -c 'service apache2 start'
```

#### dockerfile
Or you can use dockerfile to build TE driver
```bash
docker build -t tefuzz .
docker run -itd -p 80:80 -v /var/www/html/tefuzz:/var/www/html/tefuzz --name tefuzz tefuzz
```
Download data from `https://drive.google.com/file/d/1UiQ2R64hSWTqd-F7ysJ4f1cN91sqbiGO/view?usp=sharing`
decompress and put `seed` in `$YOUR_TEFUZZ_PATH/result/` folder, put `tefuzz` in `/var/www/html/` folder


### **3. Run TEFuzz**
First you need to do basic testing.
Set `TARGET_IP` to your docker ip.
```bash
python3.8 check.py
```
Then you need to change  config.py.
Set `TE_NAME` to the template engine name which you want to test.
Then RUN `python3 maim.py`.


## Publication

If you find this repository useful, please consider citing our paper.
```
@inproceedings{Yudi2023TEfuzz,
  title={Remote Code Execution from SSTI in the Sandbox:Automatically Detecting and Exploiting Template Escape Bugs},
  author={Yudi Zhao, Yuan Zhang, Min Yang},
  booktitle={{USENIX S}ecurity'23},
  year={2023}
}
```

