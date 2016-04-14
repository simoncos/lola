import sqlite3
from sklearn.svm import SVC
import time
from sklearn import cross_validation
from sklearn.metrics import f1_score, classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier as rfc
from statics import champion_counts

# Read matches: Match_id -> Participant(champion, side) & TotalChampionStats(label, ability) -> Team(win)
# 1. 10 participants as features, result following -> GG!
# 2. 2 teams's type difference as features -> GG!
# 3. Ability difference as features


# Connect database
conn = sqlite3.connect('lola.db')
cursor = conn.cursor()

#Calculate percent
cursor.execute('SELECT * FROM TotalChampionStats')
stats = cursor.fetchall()

all_stats = {}
all_stats_arr = []
names = []

for item in stats:
    name = item[0].encode('utf-8')
    names.append(name)
    kills = item[1]/(champion_counts[name])*10000
    deaths = item[2]/(champion_counts[name])*10000
    assists = item[3]/(champion_counts[name])*10000
    gold = item[4]/(champion_counts[name])
    magic = item[5]/(champion_counts[name])
    physical = item[6]/(champion_counts[name])
    true = item[7]/(champion_counts[name])
    taken = item[8]/(champion_counts[name])
    control = item[9]/(champion_counts[name])
    wardK = item[10]/(champion_counts[name])
    wardP = item[11]/(champion_counts[name])
    tmp_dict = {'kills': kills, 'assists': assists, 'assists': assists, 'gold': gold, 'magic': magic, 'physical': physical, 'true': true,
    'taken': taken, 'control': control,'wardK': wardK,'wardP': wardP,}
    tmp_arr = [gold, magic, physical, true, taken, control, wardK, wardP]
    all_stats[name] = tmp_dict
    all_stats_arr.append(tmp_arr)
print all_stats['Riven']
print all_stats['Vayne']
print all_stats['Zyra']
'''
kills = item[1]/(champion_counts[name]/100)
    deaths = item[2]/(champion_counts[name]/100)
    assists = item[3]/(champion_counts[name]/100)
    gold = item[4]/(champion_counts[name]*100)
    magic = item[5]/(champion_counts[name]*100)
    physical = item[6]/(champion_counts[name]*100)
    true = item[7]/(champion_counts[name]*100)
    taken = item[8]/(champion_counts[name]*100)
    control = item[9]/(champion_counts[name]*10)
    wardK = item[10]/(champion_counts[name]*10)
    wardP = item[11]/(champion_counts[name]*10)
'''

# Initialize set of data
all_team = []
result = []

# Select matches, champions, sides and result
st = time.time()

cursor.execute('SELECT match_id, win FROM Team WHERE side = ? LIMIT 2000 OFFSET 10000', ('blue',))
matches = cursor.fetchall()
for match in matches:
# match = (u'2053870096', 0)
    item = []
    for i in range(0, len(all_stats['Jax'])):
    item.append(50)
# item = [50, 50, 50, ...]
    cursor.execute('SELECT * FROM CountedMatch WHERE match_id = ?', (match[0].encode('utf-8'),))
    team = cursor.fetchall()
    team = team[0]
# team = (2053870096, u'Graves', u'Alistar', u'Twitch', u'Yasuo', u'Braum', u'Quinn', u'Riven', u'Zed', u'Miss Fortune', u'Zac')
    for champion in team[1:6]:
    i = 0
    for v in all_stats[champion].values():
    item[i] += v
    i += 1
    for champion in team[6:]:
    i = 0
    for v in all_stats[champion].values():
    item[i] -= v
    i += 1
    all_team.append(item)
# [[84, 26, 9, 34, 50, 51, 67, -151], ...]

    result.append(match[1])
# [1, 1, 0, ...]

print len(all_team)
print len(result)


print 'Elapsed time: %.2fs' % (time.time() - st)

st = time.time()
X_train, X_test, y_train, y_test = cross_validation.train_test_split(all_team, result, test_size=0.2, random_state=1)

# Try classifier
clf = SVC()
print 'done'
clf.fit(X_train, y_train)
result1 = clf.predict(X_test)
print classification_report(y_test, result1)
print accuracy_score(y_test, result1)
print 'Elapsed time: %.2fs' % (time.time() - st)

st = time.time()
clf2 = rfc(n_estimators=5)
clf2.fit(X_train, y_train)
result2 = clf2.predict(X_test)
print classification_report(y_test, result2)
print accuracy_score(y_test, result2)
print 'Elapsed time: %.2fs' % (time.time() - st)

cursor.close()
conn.commit()
conn.close()
