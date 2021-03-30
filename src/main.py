import compress
import random



dt=bytes([random.randint(0,10) for _ in range(1048576)])
c_dt=compress.compress(dt)
print(f"{len(dt):,} -> {len(c_dt):,} ({-(len(dt)-len(c_dt))/len(dt)*100:+.2f}%)")
d_dt=compress.decompress(c_dt)
print(f"{len(c_dt):,} -> {len(d_dt):,} ({-(len(c_dt)-len(d_dt))/len(c_dt)*100:+.2f}%)")
if (dt!=d_dt):
	raise RuntimeError("Unable to compress/decompress data!")
