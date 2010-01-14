import threading, thread, time

cond = threading.Condition()

def count():
	for i in range (0,10000):
		print i
		if i==3:
			cond.acquire()
			cond.wait()
			cond.release()
		time.sleep(1)

thread.start_new_thread(count,())
raw_input()
cond.acquire()
cond.notify()
cond.release()
raw_input()
