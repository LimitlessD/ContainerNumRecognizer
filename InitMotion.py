from time import sleep

def ShowProgress(Message, DelayT):
    print(Message)
    for x in range(0,6):
        print('. ',end='')
        sleep(DelayT/1000)
    print('完成')
    return