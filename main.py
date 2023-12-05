import datetime
import matplotlib.pyplot as plt
import scipy.stats as stats

import pandas as pd

# Встановлюємо стиль для графіків
plt.style.use('seaborn-v0_8-whitegrid')

# Зчитуємо датасет. Отримаємо основну інформацію
df = pd.read_csv('Test_task_Analyst_App.csv', sep=';')
# df.info()

# Перетворюємо гендер на числову змінну. Оскільки пропущених значень не багато, заповнюємо їх.
df['gender'] = df['gender'].apply(lambda old_gender: 0 if old_gender != 'm' else 1)

# Перетворюємо дату в справжню дату
df['time_stamp'] = pd.to_datetime(df['time_stamp'], format='%d.%m.%Y %H:%M')
df['reg_date'] = pd.to_datetime(df['reg_date'], format='%d.%m.%Y')

# Отримаємо розподіл активності користувачів по дням на основі 13-19 днів.
first_week = df[(df['time_stamp'] < datetime.datetime(2017, 3, 19, 23, 59, 59)) & (
        df['time_stamp'] > datetime.datetime(2017, 3, 13, 0, 0, 0))]
fw_group = first_week.groupby(first_week['time_stamp'].dt.date)
ax = fw_group['time_stamp'].count().plot(kind='bar', rot=0)
ax.set_xticklabels(['ПН', "ВТ", "СР", "ЧТ", "ПТ", "СБ", "НД"])

# Отримаємо записи тільки з 17 по 20
before_test = df[(df['time_stamp'] < datetime.datetime(2017, 3, 20, 23, 59, 59)) & (
        df['time_stamp'] > datetime.datetime(2017, 3, 17, 0, 0, 0))]
bf_groupA = before_test[before_test['sender_id'] % 2 == 0]
bf_groupB = before_test[before_test['sender_id'] % 2 == 1]

# Порівняємо вибірки за розподілом різних змінних

bf_uniqe_gA = bf_groupA.drop_duplicates(subset='sender_id')
bf_uniqe_gB = bf_groupB.drop_duplicates(subset='sender_id')

time_comparison = pd.concat([bf_uniqe_gA['reg_date'].describe(), bf_uniqe_gB['reg_date'].describe()], axis=1, keys=['Group A', 'Group B'])
print(time_comparison)

def distrib(column, xlabels=None):
    '''
    Функція, що будує таблицю порівняння обраного параметра.
    Будує стовбчастий графік за створеною таблицею
    :param column: назва поля, що досліджується; str
    :param xlabels: визначає підписи по осі х для графіків; list
    :return: таблиця порівняння; DataFrame
    '''
    gA = bf_uniqe_gA[column].value_counts()
    gB = bf_uniqe_gB[column].value_counts()
    gs = pd.concat([gB, gA], axis=1, keys=['groupA', 'groupB'])
    ax0 = gs.plot(kind='bar', rot=0)

    if xlabels:
        ax0.set_xticklabels(xlabels)

    gs.loc['Total'] = {'groupA': gs['groupA'].sum(), 'groupB': gs['groupB'].sum()}
    gs['diff'] = round((((gs['groupA'] / gs['groupB']) - 1) * 100), 2)
    # print(gs)

    return gs


# Перевіримо розподіл по гендеру
d_gender = distrib('gender')

# Перевіримо розподіл по платформі, на якій працює користувач
d_platform = distrib('platform_id', ['mobile', 'PC'])

# Перевіримо розподіл по даті реєстрації
d_reg_date = distrib('reg_date')


# Порівняємо кількість лайків взагалом
bf_countA = bf_groupA['time_stamp'].count()
bf_countB = bf_groupB['time_stamp'].count()
# print(bf_countB, bf_countA, bf_countB / bf_countA)

# Порівняємо кількість лайків чоловіків та жінок, на різних пристроях в тому числі
bfA = pd.pivot_table(bf_groupA, values='sender_id', index=['platform_id', 'gender'], aggfunc='count')
bfB = pd.pivot_table(bf_groupB, values='sender_id', index=['platform_id', 'gender'], aggfunc='count')
group_bf = pd.concat([bfA, bfB], axis=1, keys=['groupA', 'groupB'])

group_bf = group_bf.set_index(pd.Index(['PC, f', 'PC, m', 'mobile, f', 'mobile, m']))
count_param = lambda df, col, val: df[df[col] == val]['gender'].count()

col_1 = ('groupA', 'sender_id')
col_2 = ('groupB', 'sender_id')
group_bf.loc['Total f'] = pd.Series({col_1: count_param(bf_groupA, 'gender', 0),
                                     col_2: count_param(bf_groupB, 'gender', 0)})

group_bf.loc['Total m'] = pd.Series({col_1: count_param(bf_groupA, 'gender', 1),
                                     col_2: count_param(bf_groupB, 'gender', 1)})

group_bf.loc['Total mobile'] = pd.Series({col_1: count_param(bf_groupA, 'platform_id', 7),
                                          col_2: count_param(bf_groupB, 'platform_id', 7)})

group_bf.loc['Total PC'] = pd.Series({col_1: count_param(bf_groupA, 'platform_id', 6),
                                      col_2: count_param(bf_groupB, 'platform_id', 6)})

group_bf.loc['Total'] = pd.Series({col_1: bf_groupA['time_stamp'].count(),
                                   col_2: bf_groupB['time_stamp'].count()})

group_bf['dff'] = round((((group_bf['groupA'] / group_bf['groupB']) - 1) * 100), 2)
# print(group_bf)
# ax2 = group_bf.plot(kind='bar', rot=0, title='Порівняння кількості лайків в різних категоріях')
# ax2.legend(['Група "А"', 'Група "В"'])

# Розбиття по дням активності
gA_week = bf_groupA.groupby(bf_groupA['time_stamp'].dt.date)
gB_week = bf_groupB.groupby(bf_groupB['time_stamp'].dt.date)
# print(gA_week['time_stamp'].count())

# Побудуємо графік активності по дням
bf_weeks = pd.concat([gA_week['time_stamp'].count(), gB_week['time_stamp'].count()], axis=1, keys=['Group A', 'Group B'])

# ax3 = bf_weeks.plot(kind='bar', rot=0)
# ax3.set_xticklabels(['17.03', '18.03', '19.03', '20.03'])
# ax3.set_ylabel("Number of likes")
# ax3.set_xlabel('')

# Створимо групи для перевірки основних гіпотез експерименту
groupA = df[(df['sender_id'] % 2 == 0) & (df['time_stamp'] > datetime.datetime(2017, 3, 24, 16, 0, 0))]
groupB = df[(df['sender_id'] % 2 == 1) & (df['time_stamp'] > datetime.datetime(2017, 3, 24, 16, 0, 0))]

# Обрахуємо загальну кількість лайків
print(groupA['time_stamp'].count(), groupB['time_stamp'].count(), groupB['time_stamp'].count() / groupA['time_stamp'].count())

# Порівняємо кількість лайків чоловіків та жінок, на різних пристроях в тому числі
gA = pd.pivot_table(groupA, values='sender_id', index=['platform_id', 'gender'], aggfunc='count')
gB = pd.pivot_table(groupB, values='sender_id', index=['platform_id', 'gender'], aggfunc='count')
groups = pd.concat([gA, gB], axis=1, keys=['groupA', 'groupB'])
groups = groups.set_index(pd.Index(['PC, f', 'PC, m', 'mobile, f', 'mobile, m']))

groups.loc['Total f'] = pd.Series({col_1: count_param(groupA, 'gender', 0),
                                     col_2: count_param(groupB, 'gender', 0)})

groups.loc['Total m'] = pd.Series({col_1: count_param(groupA, 'gender', 1),
                                     col_2: count_param(groupB, 'gender', 1)})

groups.loc['Total mobile'] = pd.Series({col_1: count_param(groupA, 'platform_id', 7),
                                          col_2: count_param(groupB, 'platform_id', 7)})

groups.loc['Total PC'] = pd.Series({col_1: count_param(groupA, 'platform_id', 6),
                                      col_2: count_param(groupB, 'platform_id', 6)})

groups.loc['Total'] = pd.Series({col_1: groupA['time_stamp'].count(),
                                   col_2: groupB['time_stamp'].count()})

groups['dff'] = round((((groups['groupA'] / groups['groupB']) - 1) * 100), 2)
# print(groups)

# Побудуємо стовпчасту діаграму порівняння двох груп
ax4 = group_bf[[col_1, col_2]].plot(kind='bar', rot=0, title='Порівняння кількості лайків в різних категоріях після експерименту')
ax4.legend(['Група "А"', 'Група "В"'])


plt.show()
