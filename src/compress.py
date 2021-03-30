SIZEOF_UINT64_T=8



def bit_scan_forward(v):
	i=0
	while ((v&1)==0):
		i+=1
		v>>=1
	return i



def compress(dt):
	fl={}
	for e in dt:
		if (e not in fl):
			fl[e]=1
		else:
			fl[e]+=1
	t=tuple([0,0] for _ in range(0,256))
	mx=1
	if (len(fl)==1):
		k=list(fl.keys())[0]
		t[k][0]=1
	else:
		q=[None for _ in range(len(fl))]
		ql=0
		for c,f in fl.items():
			ql+=1
			e=[f,0,0,0,0]
			e[c//64+1]|=1<<(c%64)
			i=ql-1
			while (i>0):
				pi=(i-1)>>1
				if (((e[0]<q[pi][0]) if e[0]!=q[pi][0] else (e[1]<q[pi][1] or e[2]<q[pi][2] or e[3]<q[pi][3] or e[4]<q[pi][4]))):
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
				if (ci+1<ql and ((q[ci][0]>=q[ci+1][0]) if q[ci][0]!=q[ci+1][0] else (q[ci][1]>=q[ci+1][1] or q[ci][2]>=q[ci+1][2] or q[ci][3]>=q[ci+1][3] or q[ci][4]>=q[ci+1][4]))):
					ci+=1
				q[i]=q[ci]
				i=ci
				ci=(i<<1)+1
			while (i>0):
				pi=(i-1)>>1
				if (((e[0]<q[pi][0]) if e[0]!=q[pi][0] else (e[1]<q[pi][1] or e[2]<q[pi][2] or e[3]<q[pi][3] or e[4]<q[pi][4]))):
					q[i]=q[pi]
					i=pi
					continue
				break
			q[i]=e
			for i in range(4):
				e=ea[i+1]
				while (e!=0):
					j=bit_scan_forward(e)
					e&=~(1<<j)
					j+=i*64
					t[j][0]+=1
					if (t[j][0]>=SIZEOF_UINT64_T*8):
						print("Encoding won't fit in 64-bit integer!")
						return None
					if (t[j][0]>mx):
						mx=t[j][0]
			eb=q[0]
			for i in range(4):
				e=eb[i+1]
				while (e!=0):
					j=bit_scan_forward(e)
					e&=~(1<<j)
					j+=i*64
					t[j][1]|=(1<<t[j][0])
					t[j][0]+=1
					if (t[j][0]>=SIZEOF_UINT64_T*8):
						print("Encoding won't fit in 64-bit integer!")
						return None
					if (t[j][0]>mx):
						mx=t[j][0]
			if (ql==1):
				break
			e=(ea[0]+eb[0],ea[1]|eb[1],ea[2]|eb[2],ea[3]|eb[3],ea[4]|eb[4])
			i=0
			ci=1
			while (ci<ql):
				if (ci+1<ql and ((q[ci][0]>=q[ci+1][0]) if q[ci][0]!=q[ci+1][0] else (q[ci][1]>=q[ci+1][1] or q[ci][2]>=q[ci+1][2] or q[ci][3]>=q[ci+1][3] or q[ci][4]>=q[ci+1][4]))):
					ci+=1
				q[i]=q[ci]
				i=ci
				ci=(i<<1)+1
			while (i>0):
				pi=(i-1)>>1
				if (((e[0]<q[pi][0]) if e[0]!=q[pi][0] else (e[1]<q[pi][1] or e[2]<q[pi][2] or e[3]<q[pi][3] or e[4]<q[pi][4]))):
					q[i]=q[pi]
					i=pi
					continue
				break
			q[i]=e
	o=[((len(dt)&0x0f)<<4)|((mx+3)//4-1)]
	for i in range(0,256):
		o+=[t[i][0]]
		j=((t[i][0]+7)//8)*8
		while (j!=0):
			j-=8
			o+=[(t[i][1]>>j)&0xff]
	bf=0
	bfl=0
	for e in dt:
		e=t[e]
		i=e[0]
		while (i>0):
			j=(16 if i>16 else i)
			i-=j
			bf=(bf<<j)|((e[1]>>i)&0xffff)
			bf&=0xffffffff
			bfl+=j
			while (bfl>=8):
				bfl-=8
				o+=[(bf>>bfl)&0xff]
	if (bfl!=0):
		o+=[(bf<<(8-bfl))&0xff]
	return bytes(o)



def decompress(dt):
	i=1
	tl=((dt[0]&0x0f)+1)*4
	t=tuple([] for _ in range(0,tl))
	for j in range(0,256):
		l=dt[i]
		i+=1
		if (l>0):
			k=l-1
			l=(l+7)//8
			v=0
			while (l):
				l-=1
				v=(v<<8)|dt[i]
				i+=1
			t[k].append((v,j))
	ti=[0 for _ in range(0,tl+1)]
	for j in range(0,tl+1):
		k=j+1
		while (k<tl+1 and (k==0 or len(t[k-1])==0)):
			k+=1
		ti[j]=k-j
	o=[]
	bf=0
	bfl=0
	j=0
	e=0
	ol=dt[0]>>4
	while (True):
		if (j==0):
			if (i==len(dt)):
				break
			e=dt[i]
			i+=1
			j=8
		k=ti[bfl]
		if (k>j):
			k=j
		j-=k
		bf=(bf<<k)|((e>>j)&((1<<k)-1))
		bfl+=k
		for k in t[bfl-1]:
			if (k[0]==bf):
				o+=[k[1]]
				bf=0
				bfl=0
				break
		if (i==len(dt) and len(o)&0x0f==ol):
			break
	return bytes(o)
