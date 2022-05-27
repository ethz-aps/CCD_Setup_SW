import functools
import time
import random

#wrapper for operating device I/O in demo mode
def demo(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		if args[0].demo_mode:
			args_repr = [repr(a) for a in args]
			kwargs_repr = [f"{k}={repr(v)}" for k,v in kwargs.items()]
			signature = ", ".join(args_repr + kwargs_repr)
			print(f"DEMO call to: '{func.__name__}' with arguments: ({signature})")
			return
		else:
			return func(*args, **kwargs)
	return wrapper



def random_number():
	return random.random()