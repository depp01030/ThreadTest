#!/usr/bin/python
# -*- coding: utf-8 -*-
#%%
import threading
try:
    from Queue import Queue
except:
    from queue import Queue
import time
#%%
# 將要傳回的值存入 Queue
def worker(data, q):
    data += 30
    time.sleep(50)
    q.put(data)
#%% 
def multithread():

    q = Queue()
    worker_list = []
    data = [i for i in range(10)]
    # 使用 multi-thread
    for i in range(len(data)):
        thread = threading.Thread(target=worker, args=(i, q))
        thread.setDaemon(True)
        thread.start()
        worker_list.append(thread)
    
    # 等待全部 Thread 執行完畢


    result = []
    count = len(worker_list)
    PEEK_TIME = 1
    LAST_PEEK = time.time()
    MAX_WAITING_TIME =5
    while count > 0:
        if time.time() - LAST_PEEK > MAX_WAITING_TIME:
            print("Time out ")
            break

        if q.qsize() == 0:
            time.sleep(PEEK_TIME)
            continue
        num = q.get()
        print(num)
        count -= 1 
        #update LAST PEEK
        LAST_PEEK = time.time()  
    

    
 
'''
- 查看目前有多少個執行緒
threading.active_count()
- 查看目前使用執行緒的資訊
threading.enumerate() 
- 查看目前在哪個執行緒中
threading.current_thread()  
'''
#%%          
if __name__ == '__main__':
        
    multithread()
    print('leave function')
    