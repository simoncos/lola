import sqlite3
import pandas as pd
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
df = pd.read_sql('SELECT * FROM ChampionMatchStats', conn, index_col=['champion'])

all_stats = {}
all_stats_arr = []
names = []

for champion in df.index:
    names.append(champion)
    kills = df.ix[champion]['kills']/df.ix[champion]['picks']*1000
    deaths = df.ix[champion]['deaths']/df.ix[champion]['picks']*1000
    assists = df.ix[champion]['assists']/df.ix[champion]['picks']*1000
    gold_earned = df.ix[champion]['gold_earned']/df.ix[champion]['picks']
    magic_damage = df.ix[champion]['magic_damage']/df.ix[champion]['picks']
    physical_damage = df.ix[champion]['physical_damage']/df.ix[champion]['picks']
    true_damage = df.ix[champion]['true_damage']/df.ix[champion]['picks']
    damage_taken = df.ix[champion]['damage_taken']/df.ix[champion]['picks']
    crowd_control_dealt = df.ix[champion]['crowd_control_dealt']/df.ix[champion]['picks']*10
    ward_kills = df.ix[champion]['ward_kills']/df.ix[champion]['picks']*1000
    wards_placed = df.ix[champion]['wards_placed']/df.ix[champion]['picks']*1000
    tmp_dict = {'kills': kills, 'assists': assists, 'deaths': deaths, 'gold_earned': gold_earned, 'magic_damage': magic_damage,
        'physical_damage': physical_damage, 'true_damage': true_damage,'damage_taken': damage_taken, 'crowd_control_dealt': crowd_control_dealt,
        'ward_kills': ward_kills,'wards_placed': wards_placed}
    tmp_arr = [kills, assists, deaths, gold_earned, magic_damage, physical_damage, true_damage, damage_taken, crowd_control_dealt, ward_kills,
        wards_placed]
    all_stats[champion] = tmp_dict
    all_stats_arr.append(tmp_arr)

# Initialize set of data
all_team = []
result = []

# Select matches, champions, sides and result
st = time.time()

cursor.execute('SELECT match_id, win FROM Team WHERE side = ? LIMIT 3000 OFFSET 10000', ('blue',))
matches = cursor.fetchall()
for match in matches:
# match = (u'2053870096', 0)
    item = []
    for i in range(0, len(all_stats['Jax'])):
        item.append(0)
# item = [50, 50, 50, ...]
    cursor.execute('SELECT * FROM MatchChampion WHERE match_id = ?', (match[0].encode('utf-8'),))
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
# [[0, 0, 2, 4, 3, 51387, -921, -26326, -34600, -2184, -3876],...]

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