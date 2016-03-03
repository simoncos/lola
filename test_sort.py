import sys, csv
import operator
import pandas as pd

data = csv.reader(open('champion name.csv'), delimiter=',')
s = sorted(data, key=operator.itemgetter(0), reverse=False)

with open('sorted champion.csv','wb') as f:
    writer = csv.writer(f, delimiter=',')
    for i in range(128):
        writer.writerow(s[i])
    
print s

df = pd.read_csv('test.csv', sep=',', header=0, index_col=0)

# df = pd.DataFrame(columns = s)
