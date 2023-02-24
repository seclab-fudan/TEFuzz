# TEFuzz 
This repository provides the tool for the paper "Remote Code Execution from SSTI in the Sandbox: Automatically Detecting and Exploiting Template Escape Bugs" accepted at USENIX Security '23.

Table of Contents
=================
* [Requirements](#requirements)
* [Getting Started Instructions](#getting-started-instructions)
  * [Docker Setup](#docker-setup)
  * [Build from Scratch](#build-from-scratch)
* [Publication](#publication)

## Requirements

* OS: 
  - TEFuzz is developed and tested under Ubuntu 18.04.
* Python3 (>= 3.8)
* Docker (optional, for [Docker Setup](#docker-setup) only)

## Structure

## Getting Started Instructions



### **0. Install dependencies**

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
pip3 install -r requirements.txt
```

#### **1. Clone the TEFuzz repository**

```git
git clone https://github.com/seclab-fudan/TEFuzz
```

#### **2. Build docker**
For convenience, we provide a docker image for the Target TE environment.

```bash
docker pull altm4nz/tefuzz:latest
docker run -itd --name tefuzz altm4nz/tefuzz
```

#### **3. Run TEFuzz**

First you need to change config.py.
Set `TARGET_IP` to your docker ip.
Set `TE_NAME` to the template engine name which you want to test.
Set `BASE_TE_PATH` to your web directory.
Then RUN `python3 maim.py`.


## Publication

If you find this repository useful, please consider citing our paper.

