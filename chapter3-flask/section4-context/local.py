# coding=utf-8
import threading

# 本地线程实现的原理就是：在threading.current_thread().__dict__里添加一个包含对象mydata的id值的key，来保存不同线程的状态

mydata = threading.local()
mydata.number = 42
print mydata.number
log = []


def f():
    mydata.number = 11
    log.append(mydata.number)


thread = threading.Thread(target=f)
thread.start()
thread.join()
print log
print mydata.number

# 42
# [11]      #在线程内变成了mydata.number其他的值
# 42        #但是没有影响到开始设置的值
