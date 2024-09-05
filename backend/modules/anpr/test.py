from main import ANPR
from os import listdir
import time

file = "sample_2.png"

print(f"{file}")
plate = (ANPR(f"{file}"))
print("File:", file, "Plate:", str(plate))
with open(f"{file}.txt","w") as f:
	f.write(str(plate))
