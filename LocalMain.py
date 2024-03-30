#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
try:
    # no module in py23
    import requests
    import json
except:
    pass
import re
import traceback

import threading
try:
    from Queue import Queue
except:
    from queue import Queue
import time

from utils import setting_initialize, add_pre, add_post, get_step_list
from InfoConverter.UnitGeomClass import UnitPoint
from InfoConverter.CAMClass import CAMCollection, CAMwkt
from InfoConverter.InfoConverterAPI import create_layer_by_collection

import genClasses
from Record import Record
record = Record()


#%%
from project_utils import del_layer
from DataMerge import data_merge
from DataExtraction import data_extraction
#%%
SERVICE_ROOT = 'http://ws125:3114/cam/converter_service/'
#%%

def get_common_pack():
    common_pack = {
        'project_name' : 'INSpaing',
        'job_name' : 'tsmc'
    }
    return common_pack
def get_layer_pack(layer_name):
    layer_pack = {
        'layer_name' : layer_name,
        'layer_info' : [layer_name],
        'check_list' : []
    }
    return layer_pack



def post_to_service(output_dict,
                    return_info_queue):

    # record.info('Post data to service')
    # data_dict = {'data_dict' : str(output_dict)}
    # record.info('Get data from service')
    service_function_name = 'cam_template'
    url = SERVICE_ROOT + service_function_name
    
    return_info_queue.put(output_dict['layer_pack']['layer_name'])
    '''
    thread = threading.Thread(target=post_to_service,
                            args=(post_pack,
                                    return_info_queue))
    thread.setDaemon(True)
    thread.start()
    '''
    # r = requests.post(url, data = data_dict)
    # return_dict = eval(r.text)

    # if type(return_dict) == dict and  'Traceback' in return_dict.keys():
    #     return_dict['Traceback'].split('\n')
    #     record.info(str(return_dict.values()))
    #     record.error(str(return_dict.keys()))
    return return_info_queue
#%%
def step_work(step_object, affect_layer_list):
    try:
        ''' =============== DataExtraction =============== '''
        '''
        這個區塊要抽資料，並透過thread 的方式傳送到服務端運算
        1. init threading stuff
        2. get common data pack
        3. loop affected layers and get layer pack 
        4. post to service
        '''
        affect_layer_list = ['l2', 'l3', 'l4']
        ## init threading stuff
        worker_list = []
        return_info_queue = Queue()
        ## get common data pack

        common_pack = get_common_pack()
        # loop affectd layers
        for layer_name in affect_layer_list:
            #get layer pack
            layer_pack = get_layer_pack(layer_name)
            #create thread for post to service  
            post_pack = {
                'common_pack' : common_pack,
                'layer_pack' : layer_pack
                }
            post_to_service(post_pack,
                            return_info_queue)

 
        ''' ================== Cam Action ================= '''
        '''
        1. 接收return 資訊
        2. 執行cam 軟體 cam action
        '''
        result = []
        count = len(affect_layer_list)
        PEEK_TIME = 1
        LAST_PEEK = time.time()
        MAX_WAITING_TIME =5
        while count > 0:
            if time.time() - LAST_PEEK > MAX_WAITING_TIME:
                print("Time out ")
                break

            if return_info_queue.qsize() == 0:
                time.sleep(PEEK_TIME)
                continue
            num = return_info_queue.get()
            print(num)
            count -= 1 
            #update LAST PEEK
            LAST_PEEK = time.time()  


        record.info('Step : {0} finish '.format(step_object.name))
    except Exception as  err_msg:
        err_msg = traceback.format_exc()
        print(err_msg)
        record.error(err_msg)

def get_affect_layer_list(pcb_object):
    layer_list = []
    try:
        pcb_object.COM('get_affect_layer')
        affect_layer_string = pcb_object.COMANS
        layer_list = affect_layer_string.split() 
    except Exception as e:
        err_msg = traceback.format_exc()
        print(err_msg)

    return layer_list
#%%

def main(config):
    try:
        job_object = genClasses.Job(os.environ['JOB'])
        pcb_object = job_object.steps['pcb']

        if os.environ['EXEC_MODE'] == 'Auto':
            step_list = get_step_list(job_object, 'pcb')
        elif os.environ['EXEC_MODE'] == 'Manual':
            step_list = [os.environ['STEP']]

        ''' ================ prepare info ================ '''
        affect_layer_list = get_affect_layer_list(pcb_object)
        ''' =============================================== '''
        for step_name in step_list:
            '''
            step_name = 'pcb'
            '''
            step_object = job_object.steps[step_name]

            step_object.open()

            step_work(step_object, affect_layer_list)

            step_object.close()
        
        del_layer(job_object)
        pcb_object.open()

        ' ================== 併板 check ================== '
        if len(step_list) > 1 and os.environ['EXEC_MODE'] == 'Manual':
            record.warning('此案件為併板，請確認是否都執行')
        ' ============================================== '

    except Exception as  e:
        err_msg = traceback.format_exc()
        print(err_msg)
        record.error(err_msg)




'''
# for debug
with open('job_basic_data_dict.json', 'r') as f:
    job_basic_data_dict = eval(f.read())

data_dict = {'job_basic_data_dict' : str(job_basic_data_dict)}

url = 'http://ws125:3114/test/cam_template_service'
r = requests.post(url, data = data_dict)

return_dict = call_service(data_dict)

'''