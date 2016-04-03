import sqlite3
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from scipy import spatial
import matplotlib.pyplot as plt

#All fields' name
fields = ['gold_earned', 'magic_damage', 'physical_damage', 'true_damage', 'damage_taken','crowd_control_dealt', 'ward_kills', 'wards_placed']
fields_total = ['total_gold_earned','total_magic_damage','total_physical_damage', 'total_true_damage', 'total_damage_taken',
		'total_crowd_control_dealt','total_ward_kills','total_wards_placed']
fields_percent = ['gold_percent', 'magic_percent','physical_percent', 'true_percent', 'taken_percent', 'control_percent', 'wardK_percent',
		'wardP_percent']

def count_avg_dict(label):
	tmp_dict = {'gold_percent': 0, 'magic_percent': 0,'physical_percent': 0, 'true_percent': 0, 'taken_percent': 0, 'control_percent': 0,
		'wardK_percent': 0, 'wardP_percent': 0,}
	for name in label_dict[label]:
		for key in tmp_dict.keys():
			tmp_dict[key] += all_stats[name][key]
	for key in tmp_dict.keys():
		tmp_dict[key] /= len(label_dict[label])
	return tmp_dict

def count_avg_arr(label):
	tmp_arr = [0,0,0,0,0,0,0,0]
	for name in new_label_dict[label]:
		for i in range(0, len(fields_percent)):
			tmp_arr[i] += all_stats[name][fields_percent[i]]
	for i in range(0,len(tmp_arr)):
		tmp_arr[i] /= len(new_label_dict[label])
	return tmp_arr


conn = sqlite3.connect('lola.db')
cursor = conn.cursor()

#Calculate percent
cursor.execute('SELECT * FROM TotalChampionStats')
stats = cursor.fetchall()

all_stats = {}
all_stats_arr = []
names = []

for item in stats:
	name = item[0]
	names.append(item[0].encode('utf-8'))
	#kills_percent = 100*item[1]/item[12]
	#deaths_percent = 100*item[2]/item[13]
	#assists_percent = 100*item[3]/item[14]
	gold_percent = 100*item[4]/item[15]
	magic_percent = 100*item[5]/item[16]
	physical_percent = 100*item[6]/item[17]
	true_percent = 100*item[7]/item[18]
	taken_percent = 100*item[8]/item[19]
	control_percent = 100*item[9]/item[20]
	wardK_percent = 100*item[10]/item[21]
	wardP_percent = 100*item[11]/item[22]
	tmp_dict = {'gold_percent': gold_percent, 'magic_percent': magic_percent, 'physical_percent': physical_percent, 'true_percent': true_percent,
		'taken_percent': taken_percent, 'control_percent': control_percent,'wardK_percent': wardK_percent,'wardP_percent': wardP_percent,}
	tmp_arr = [gold_percent, magic_percent, physical_percent, true_percent, taken_percent, control_percent, wardK_percent, wardP_percent]
	all_stats[name] = tmp_dict
	all_stats_arr.append(tmp_arr)
#for (k, v) in all_stats.items():
#	print k, '\n', v

#------------------k-means------------------#
meandistortions = []
num_clusters = 6
km = KMeans(n_clusters=num_clusters, max_iter=100, n_init=100)
km.fit(all_stats_arr)

label_dict = []
for i in range(0, num_clusters):
	label_dict.append([])
i = 0
for label in km.labels_:
	label_dict[label].append(names[i])
	print names[i], int(label)	
	cursor.execute('UPDATE TotalChampionStats SET label=? WHERE champion=?', (int(label), names[i],))
	i += 1
#Show clustering results and average statistics
#for i in range(0, len(label_dict)):
	#print label_dict[i]
	#print count_avg_dict(i), '\n'
centers = km.cluster_centers_.tolist()
sum_dist = 0
for label in range(0, num_clusters):
	for name in label_dict[label]:
		sum_dist += spatial.distance.euclidean(all_stats_arr[names.index(name)], centers[label])
#print num_clusters, sum_dist/128
	
#Calculate distance between clusters
dist_cluster = 0
num_normalize = 0
for i in range(0, num_clusters):
	for j in range(i+1, num_clusters):
		dist_cluster += spatial.distance.euclidean(centers[i], centers[j])
		num_normalize += 1
print 'k-means\nnumber of clusters:', num_clusters
print 'distortion:', sum_dist/128
print 'distance betweeen clusters/distortion: %.5f\n' % (dist_cluster/(num_normalize*sum_dist/128))
'''
meandistortions.append(dist_cluster/(num_normalize*sum_dist/128))
plt.plot(num_clusters, meandistortions, 'bx-')
plt.xlabel('k')
plt.ylabel('Average distance of clusters/distortion')
plt.title('Selecting k with the Elbow Method')
plt.show()
'''

#------------------agglomerative------------------#
meandistortions = []
num_clusters = 6
ward = AgglomerativeClustering(n_clusters=num_clusters, linkage='complete')
ward.fit(all_stats_arr)
new_label_dict = []
for i in range(0, num_clusters):
	new_label_dict.append([])
i = 0
for label in ward.labels_:
	new_label_dict[label].append(names[i])
	i += 1
#Show clustering results and average statistics
'''for i in range(0, len(new_label_dict)):
	#print new_label_dict[i]
	#print count_avg_arr(i)
	print label_dict[i]
	print count_avg_dict(i), '\n'
'''

#Find centroids
centroids = []
for i in range(0, num_clusters):
	centroids.append(count_avg_arr(i))
sum_dist = 0
#Calcultate distortions
for i in range(0, num_clusters):
	for name in new_label_dict[i]:
		sum_dist += spatial.distance.euclidean(all_stats_arr[names.index(name)], centroids[i])
#print num, sum_dist/128
#meandistortions.append(sum_dist/128)

#Calculate distance between clusters
dist_cluster = 0
num_normalize = 0
for i in range(0, num_clusters):
	for j in range(i+1, num_clusters):
		dist_cluster += spatial.distance.euclidean(centroids[i], centroids[j])
		num_normalize += 1
print 'agglomerative clustering\nnumber of clusters:', num_clusters
print 'distortion:', sum_dist/128
print 'distance betweeen clusters/distortion: %.5f' % (dist_cluster/(num_normalize*sum_dist/128))

'''
print all_stats['Rumble']
print all_stats['Orianna']
print all_stats['Anivia']

meandistortions.append(dist_cluster/(num_normalize*sum_dist/128))
plt.plot(num_clusters, meandistortions, 'bx-')
plt.xlabel('n')
plt.ylabel('Average distance of clusters/distortion')
plt.title('Selecting n with the Elbow Method\nin Agglomerative Clustering')
plt.show()
'''
cursor.close()
conn.commit()
conn.close()