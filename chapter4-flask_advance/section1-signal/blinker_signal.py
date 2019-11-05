# coding=utf-8
from blinker import signal

# 可以设想，connect和send这两个方法不放在一个文件中，它们通过started作为桥梁达到解耦的作用
started = signal('test-started')


def each(round):
    print 'Round {}!'.format(round)


def round_two(round):
    print 'Only {}'.format(round)


# connect是订阅信号的方法。第二个参数是可选的，用于确定信号的发送端。“started.connect(round_two, sender=2)”表示值为2的时候才会接收
started.connect(each)
started.connect(round_two, sender=2)

for round in range(1, 4):
    started.send(round)
# Round 1!
# Round 2!
# Only 2
# Round 3!
