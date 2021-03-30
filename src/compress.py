SIZEOF_UINT16_T=2



def compress(dt):
	def _less(a,b):
		if (a[0]!=b[0]):
			return a[0]<b[0]
		for i in range(0,len(a[1])):
			if (i==len(b[1])):
				return False
			if (a[1][i]!=b[1][i]):
				return a[1][i]<b[1][i]
		return len(a[1])<len(b[1])
	fl={}
	for e in dt:
		if (e not in fl):
			fl[e]=1
		else:
			fl[e]+=1
	t=tuple([0,0] for _ in range(0,256))
	if (len(fl)==1):
		k=list(fl.keys())[0]
		t[k][0]=1
	else:
		q=[None for _ in range(len(fl))]
		ql=0
		for c,f in fl.items():
			ql+=1
			e=(f,bytes([c]))
			i=ql-1
			while (i>0):
				pi=(i-1)>>1
				if (_less(e,q[pi])):
					q[i]=q[pi]
					i=pi
					continue
				break
			q[i]=e
		while (True):
			ea=q[0]
			e=q.pop()
			ql-=1
			i=0
			ci=1
			while (ci<ql):
				if (ci+1<ql and not _less(q[ci],q[ci+1])):
					ci+=1
				q[i]=q[ci]
				i=ci
				ci=(i<<1)+1
			while (i>0):
				pi=(i-1)>>1
				if (_less(e,q[pi])):
					q[i]=q[pi]
					i=pi
					continue
				break
			q[i]=e
			eb=q[0]
			for k in ea[1]:
				t[k][0]+=1
				if (t[k][0]>=SIZEOF_UINT16_T*8):
					print("Encoding won't fit in 'uint16_t'!")
					return None
			for k in eb[1]:
				t[k][1]|=(1<<t[k][0])
				t[k][0]+=1
				if (t[k][0]>=SIZEOF_UINT16_T*8):
					print("Encoding won't fit in 'uint16_t'!")
					return None
			if (ql==1):
				break
			e=(ea[0]+eb[0],bytes(sorted(ea[1]+eb[1])))
			i=0
			ci=1
			while (ci<ql):
				if (ci+1<ql and not _less(q[ci],q[ci+1])):
					ci+=1
				q[i]=q[ci]
				i=ci
				ci=(i<<1)+1
			while (i>0):
				pi=(i-1)>>1
				if (_less(e,q[pi])):
					q[i]=q[pi]
					i=pi
					continue
				break
			q[i]=e
	o=[len(dt)&0xff]
	for i in range(0,256):
		o+=[t[i][0]]
		if (t[i][0]>8):
			o+=[t[i][1]>>8,t[i][1]&0xff]
		elif (t[i][0]>0):
			o+=[t[i][1]]
	bf=0
	bfl=0
	for e in dt:
		e=t[e]
		bf=(bf<<e[0])|e[1]
		bf&=0xffffff
		bfl+=e[0]
		while (bfl>=8):
			bfl-=8
			o+=[(bf>>bfl)&0xff]
	if (bfl!=0):
		o+=[(bf<<(8-bfl))&0xff]
	return bytes(o)



def decompress(dt):
	ol=dt[0]
	i=1
	t=tuple([] for _ in range(0,15))
	for j in range(0,256):
		l=dt[i]
		i+=1
		if (l>8):
			t[l-1].append(((dt[i]<<8)|dt[i+1],j))
			i+=2
		elif (l>0):
			t[l-1].append((dt[i],j))
			i+=1
	o=[]
	bf=0
	bfl=0
	j=0
	e=0
	while (True):
		if (j==0):
			if (i==len(dt)):
				break
			e=dt[i]
			j=8
			i+=1
		j-=1
		bf=(bf<<1)|((e>>j)&1)
		bfl+=1
		for k in t[bfl-1]:
			if (k[0]==bf):
				o+=[k[1]]
				bf=0
				bfl=0
				break
		if (i>=len(dt)-2 and len(o)&0xff==ol):
			break
	return bytes(o)
