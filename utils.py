import functools
import time

#wrapper for operating device I/O in demo mode
def demo(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		if args[0].demo_mode:
			args_repr = [repr(a) for a in args]
			kwargs_repr = [f"{k}={repr(v)}" for k,v in kwargs.items()]
			signature = ", ".join(args_repr + kwargs_repr)
			print(f"DEMO call to: {func.__name__} with arguments: ({signature})")
			return
		else:
			return func(*args, **kwargs)
	return wrapper

def timer(func):
	'''Prints the runtime of the decorated function (alternatively to timeit)'''
	@functools.wraps(func)
	def wrapper_timer(*args, **kwargs):
		t0 = time.perf_counter()
		value = func(*args, **kwargs)
		t1 = time.perf_counter()
		print(f'Execution time of {func} was {(t1-t0):.4f} s.')
		return value
	return wrapper_timer
