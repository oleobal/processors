"""
Demo program for the v16a
"""
from v16alpha.v16alpha import V16alpha
from v16alpha.v16alpha_util import *

from time import sleep

def pingPong():
	"""
	"bounces" a 1 across the I/O pins
	"""
	
	rioAonly="""
	Lstore 0x8000
	store rint rioa
	
	:goRight:
	RIOA >> 1
	IF RIOA > 1
	STORE !goRight RCNT
	
	:goLeft:
	RIOA << 1
	IF RIOAL < 0x80
	STORE !goLeft RCNT
	
	
	STORE !goRight RCNT
	"""
	
	
	rioAandB="""
	Lstore 0x8000
	store rintL riob
	Lstore 0
	store rint rioa
	
	:goRightB:
	RIOB >> 1
	IF RIOB > 1
	STORE !goRightB RCNT
	
	store 0 riob
	store 0x80 rioal
	
	:goRightA:
	RIOA >> 1
	IF RIOA > 1
	STORE !goRightA RCNT
	
	:goLeftA:
	RIOA << 1
	IF RIOAL < 0x80
	STORE !goLeftA RCNT
	
	store 0 rioal
	store 1 riob
	
	:goLeftB:
	RIOB << 1
	IF RIOB < 0x80
	STORE !goLeftB RCNT
	

	STORE !goRightB RCNT
	"""
	
	p = V16alpha()
	loadProgram(p,rioAandB)
	
	while (p.err.value < 9):
		p.pinset.setPinState(0,True)

		sleep(0.01)
		print(p.pinset, end="\r", flush=True)
		
if __name__ == "__main__" :
	pingPong()