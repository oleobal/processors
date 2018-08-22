def Register(int):
	def __new__(S, size, *args, **kwargs):
		r = super(Register, S).__new__(S, 0)
		r.maxVal = 2**size
		return r
	
	def __str__(self):
		return "hello"+str(self.maxVal)
	def __repr__(self):
		return "Register "+str(self.maxVal)
		
r = Register.__new__(Register, 16) ; print(r)