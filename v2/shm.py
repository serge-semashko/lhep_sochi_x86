import time
import memcache
def run_loop():
    client = memcache.Client([('127.0.0.1', 11211)])
    value = input("Press key to continue \n")
    for i in range(0,20000):
        sendvalue = str(i)
        client.set('Value', sendvalue)
        print("sent value  ",sendvalue)
        time.sleep(2)

if __name__ == "__main__":
    run_loop()
