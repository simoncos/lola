import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from scipy import spatial
import matplotlib.pyplot as plt

#All fields' name
fields = ['kills', 'deaths', 'assists', 'gold_earned', 'magic_damage', 'physical_damage', 'true_damage', 'damage_taken',
    'crowd_control_dealt', 'ward_kills', 'wards_placed']
fields_total = ['total_gold_earned','total_magic_damage','total_physical_damage', 'total_true_damage', 'total_damage_taken',
        'total_crowd_control_dealt','total_ward_kills','total_wards_placed']
fields_percent = ['gold_percent', 'magic_percent','physical_percent', 'true_percent', 'taken_percent', 'control_percent', 'wardK_percent',
        'wardP_percent']

def count_avg_dict(label):
    tmp_dict = {'kills': 0, 'deaths': 0, 'assists': 0, 'gold_earned': 0, 'magic_damage': 0, 'physical_damage': 0, 'true_damage': 0,
        'damage_taken': 0, 'crowd_control_dealt': 0, 'ward_kills': 0, 'wards_placed': 0}
    for name in label_dict[label]:
        for key in tmp_dict.keys():
            tmp_dict[key] += all_stats[name][key]
    for key in tmp_dict.keys():
        tmp_dict[key] /= len(label_dict[label])
    return tmp_dict

def count_avg_arr(label):
    tmp_arr = [0,0,0,0,0,0,0,0,0,0,0]
    for name in new_label_dict[label]:
        for i in range(0, len(fields)):
            tmp_arr[i] += all_stats[name][fields[i]]
    for i in range(0,len(tmp_arr)):
        tmp_arr[i] /= len(new_label_dict[label])
    return tmp_arr

#  iterate all champions' name, retrieve every column by fields' name, calculate the average stats per game of each champions
conn = sqlite3.connect('lola.db')
cursor = conn.cursor()
df = pd.read_sql('SELECT * FROM ChampionMatchStats', conn, index_col=['champion'])

all_stats = {}
all_stats_arr = []
names = []

for champion in df.index:
    names.append(champion)
    kills = df.ix[champion]['kills']/df.ix[champion]['picks']
    deaths = df.ix[champion]['deaths']/df.ix[champion]['picks']
    assists = df.ix[champion]['assists']/df.ix[champion]['picks']
    gold_earned = df.ix[champion]['gold_earned']/df.ix[champion]['picks']
    magic_damage = df.ix[champion]['magic_damage']/df.ix[champion]['picks']
    physical_damage = df.ix[champion]['physical_damage']/df.ix[champion]['picks']
    true_damage = df.ix[champion]['true_damage']/df.ix[champion]['picks']
    damage_taken = df.ix[champion]['damage_taken']/df.ix[champion]['picks']
    crowd_control_dealt = df.ix[champion]['crowd_control_dealt']/df.ix[champion]['picks']
    ward_kills = df.ix[champion]['ward_kills']/df.ix[champion]['picks']
    wards_placed = df.ix[champion]['wards_placed']/df.ix[champion]['picks']
    tmp_dict = {'kills': kills, 'assists': assists, 'deaths': deaths, 'gold_earned': gold_earned, 'magic_damage': magic_damage,
        'physical_damage': physical_damage, 'true_damage': true_damage,'damage_taken': damage_taken, 'crowd_control_dealt': crowd_control_dealt,
        'ward_kills': ward_kills,'wards_placed': wards_placed}
    tmp_arr = [kills, assists, deaths, gold_earned, magic_damage, physical_damage, true_damage, damage_taken, crowd_control_dealt, ward_kills,
        wards_placed]
    all_stats[champion] = tmp_dict
    all_stats_arr.append(tmp_arr)

#for (k, v) in all_stats.items():
#   print k, '\n', v

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
    #print names[i], int(label) 
    cursor.execute('UPDATE ChampionMatchStats SET label=? WHERE champion=?', (int(label), names[i],))
    i += 1
#Show clustering results and average statistics
for i in range(0, len(label_dict)):
    print label_dict[i]
    print count_avg_dict(i), '\n'
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