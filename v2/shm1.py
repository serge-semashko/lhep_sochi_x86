import time
import memcache
client = memcache.Client([('127.0.0.1', 11211)])
def run_loop():
    value = input("Press key to continue \n")
    result = client.get('some_key')
    for i in range(0,20000):
        sendvalue = client.get('Value')
        print("get value  ",sendvalue)
        time.sleep(2)

if __name__ == "__main__":
    run_loop()
