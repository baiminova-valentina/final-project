
# # Анализ "Ненужные вещи"

# ## Описание данных:

# 
# 
# Описание данных:
#   Датасет содержит данные о событиях, совершенных в мобильном приложении
# "Ненужные вещи". В нем пользователи продают свои ненужные вещи, размещая их на доске объявлений.    
# 
# В датасете содержатся данные пользователей, впервые совершивших действия в приложении после 7 октября 2019 года.  
# Колонки в /datasets/mobile_sources.csv :  
# userId — идентификатор пользователя,  
# source — источник, с которого пользователь установил приложение.  
# Колонки в /datasets/mobile_dataset.csv :  
# event.time — время совершения,  
# user.id — идентификатор пользователя,  
# event.name — действие пользователя.  
# Виды действий:  
# advert_open — открыл карточки объявления,  
# photos_show — просмотрел фотографий в объявлении,  
# tips_show — увидел рекомендованные объявления,  
# tips_click — кликнул по рекомендованному объявлению,  
# contacts_show и show_contacts — посмотрел номер телефона,  
# contacts_call — позвонил по номеру из объявления,  
# map — открыл карту объявлений,  
# search_1 — search_7 — разные действия, связанные с поиском по сайту,  
# favorites_add — добавил объявление в избранное.
# 
# 
# Цели исследования  
# Установить цель исследования  
# Предобработка данных
# - Проверить данные  на наличие пропусков и дубликатов
# - Проверить совпадает ли количество уникальных пользователей в обеих базах данных? 
# - Переименовать название столбцов
# - Объединить базы данные по user_id
# 
# 
# Исследовательский анализ данных
# - Сколько уникальных событиях? Выстроить таблицу с количеством каждого лога.
# - Сколько уникальных пользователей
# - Проверить данными за какой период у нас?
# - Оценить статистику прибытия новых пользователей с течением времени
# - Рассчитываем воронку событий. Считаем конверсии
# 
# 
# 
# Основные вопросы исследования:
# 
# 1 Проанализируйте связь целевого события — просмотра контактов — и других действий пользователей:    
# 
#     -В разрезе сессий отобрать сценарии\паттерны, которые
#     приводят к просмотру контактов  
#     -Построить воронки по основным сценариям в разрезе
#     уникальных пользователей    
#     
# 2 Оцените, какие действия чаще совершают те пользователи, которые просматривают контакты:  
# 
#     - Рассчитать относительную частоту событий в разрезе двух групп пользователей:  
#     
#         a группа пользователей, которые смотрели
#         контакты contacts_show
#         b группа пользователей, которые не смотрели
#         контакты contacts_show
# 
#   
# 3 Проверка гипотез
# 
#     a. Одни пользователи совершают действия tips_show и tips_click , другие —только tips_show . Проверьте гипотезу: конверсия в просмотры контактов различается у этих двух групп.
# 
#     Гипотеза
# - H0 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click равна конверсии в просмотры  группы пользователей совершающие только tips_show 
# - H1 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры  группы пользователей совершающие только tips_show 
# 
# 
# 
#     b. Конверсия в просмотры группы пользователей  воспользовавшихся функцией map больше, чем у группы пользователей, которые не пользовались ей.
#     
#     Гипотеза
# - H0 -  конверсия в просмотры группы пользователей совершающие действие map равна конверсии в просмотры группы пользователей, которые это действие не совершили
# - H1 - конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили
# 
# 

# ## Импорт библиотек. Предобработка данных.

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from tqdm import tqdm
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats as st
import math as mth


# У нас две базы данных source и data . Загрузим и изучим их.

# In[2]:


data=pd.read_csv('https://code.s3.yandex.net/datasets/mobile_dataset.csv')
data


# In[3]:


source=pd.read_csv('https://code.s3.yandex.net/datasets/mobile_sources.csv')
source


# Проверим на пропуски и дубпликаты

# In[4]:


def initial_analysis(data):
    print(data.head())
    print(data.info())
    for col in data.columns:
        data_nulls= np.mean(data[col].isnull())
        print('Количество пропусков:{} - {}%'.format(col, round(data_nulls*100)))
    print('Количество дубликатов в таблице:{}%'.format(round(data.duplicated().sum()*100)))


# In[5]:


initial_analysis(data)


# In[6]:


initial_analysis(source)


# Видим, что отсутсвтуют дубпликаты и пропуск таблицах. Приступим к обработке данных


# Переименуем столбцы

# In[7]:


source.columns=['user_id', 'source_engine',]


# In[8]:


data.columns=['event_time','event_name','user_id']


# Проверим совпаают ли список пользователей в обеих таблицах

# In[9]:


data['user_id'].nunique()


# In[10]:


source['user_id'].nunique()


# Смешиваем таблицы

# In[11]:


data=data.merge(source, on='user_id',how='left')


# Приводим столбец ос временем к нужному формату.

# In[12]:


data['event_time'] = pd.to_datetime(data['event_time'])
data['event_time'] = data['event_time'].dt.round('S')


# Проверим на дубпликаты уникальный действия

# In[13]:


data['event_name'].unique()


# Видим, что есть одинаковые действия записанные по разному. Переименуем

# In[14]:


data['event_name'] = data['event_name'].replace('show_contacts', 'contacts_show')



# ОбЪедним лог 'search_1', 'search_2', 'search_3',  'search_4', 'search_5', 'search_6', 'search_7', в один лог search

# In[15]:


data['event_name'] = data['event_name'].replace('search_1','search')
data['event_name'] = data['event_name'].replace('search_2','search')
data['event_name'] = data['event_name'].replace('search_3','search')
data['event_name'] = data['event_name'].replace('search_4','search')
data['event_name'] = data['event_name'].replace('search_5','search')
data['event_name'] = data['event_name'].replace('search_6','search')
data['event_name'] = data['event_name'].replace('search_7','search')




# Проверим, что период данных соответсвует заявленному в описании.

# In[16]:


print('Минамальное время:',data['event_time'].min(), 'Максимальное время:',data['event_time'].max())


# Вывод по шагу  
# - Проверили на пропуски и дубпликаты. ничего не нашли  
# - Переименовали столбцы.   
# - Объединили значения contacts_show и show_contacts    
# - Объединили  'search_1', 'search_2', 'search_3', 'search_4', 'search_5', 'search_6', 'search_7', в один лог search  
# - привели столбец с датами к нужному формату  
# - Проверили что период данных соответсвует заявленному в описании.
# 
# 

# ## Исследуем данные

# ### Посмотрим количество логов

# In[17]:


event_data=data['event_name'].value_counts().reset_index()
event_data.columns=['event_name','count']


# In[18]:


# Make a random dataset:
plt.figure(figsize=(10, 6))
sns.barplot(x = 'event_name', y = 'count', data = event_data )
plt.title('Распределение логов')
plt.xlabel('Логи')
plt.ylabel('Количество логов')
plt.xticks(rotation = 90)
plt.show()



# ### Изучим активность пользователей

# Самые активные пользователи

# In[19]:


events_by_users=data.groupby('user_id')['event_name'].count().sort_values(
    ascending=False).reset_index()
events_by_users.head(15)


# In[20]:


ax=events_by_users.head(15)
plt.figure(figsize=(10, 5))
sns.barplot(x='user_id', y='event_name', data=ax)
sns.set_palette('muted')
plt.title('Количество действий у самых активных пользователей')
plt.xlabel('Пользователи')
plt.ylabel('Количество действий')
plt.xticks(rotation = 90)
plt.show()




# In[21]:


events_by_users.describe()


# Здесь мы вилим, что в среднем пользователь соверашает 17 действий, а медианное значение говорит,что 9 действий. Минимальное количество действий это 1

# ### Проверим количество пользовтелей по времени.

# In[22]:


activity_data=data
activity_data['activity_day']=data['event_time'].dt.date
activity_data


# In[23]:


activity_data=pd.pivot_table(data,
               index=["activity_day"],
               values=["user_id"],
               aggfunc='nunique').reset_index()
activity_data.columns=['activity_date', 'user_count']

plt.figure(figsize=(10, 5))
sns.barplot(x='user_count', y='activity_date', data=activity_data)
sns.set_palette('muted')
plt.title('Динамика посещений сайта ')
plt.xlabel('Количество уникальных пользователей')
plt.ylabel('День')
plt.show()


# Видим, что активность пользователей сильно меньше была 12 октября и также сильны провал в активности наблюдался в 2 ноября. Проверив календарь, видим, что оба дня были субботами. Надо преврить активность по дням недели. 

# In[24]:


activity_weekday=data
activity_weekday['activity_weekday']=activity_weekday['event_time'].dt.weekday
activity_weekday


# In[25]:


activity_weekday_table=pd.pivot_table(activity_weekday,
               index=["activity_weekday"],
               values=["user_id"],
               aggfunc='nunique').reset_index()
activity_weekday_table.columns=['activity_weekday', 'user_count']


# In[26]:


plt.figure(figsize=(10, 5))
sns.barplot(x='activity_weekday', y='user_count', data=activity_weekday_table)
sns.set_palette('muted')
plt.title('Динамика посещений сайта')
plt.xlabel('День недели')
plt.ylabel('Количество уникальных пользователей')
plt.show()



# Видим заметное проседание в активности во второй половине недели, в особенности в субботу.

# Активность пользователей с течением времени

# In[27]:


dau=data.groupby('activity_day').agg({'event_name':'count'})
sns.set_theme()
sns.set_palette('muted')
sns.set(rc={'figure.figsize':(10,5)})
plt.plot(dau)
plt.title('Активность пользователей с течением времени')
plt.xlabel('Дата')
plt.ylabel('Количество  действий')
plt.show()


# Проверим активность пользователей в течение времени. Тут видим сильное просидание в кол-во пользовтелях в приложении 12 октября и 2 ноября, возможно в эти даты происходил массовый сбой в приложениях, что повлияло на количество пользователей. И цикличность проседаний по выходным

# Подсчет сессий, создаем колонку session_id

# In[28]:


data=data.sort_values(['user_id', 'event_time'])


# In[29]:


data.head(15)


# In[30]:


#convert to datetimes
data['event_timestamp'] = pd.to_datetime(data['event_time'])
#identify difference 5Min for each group with cumulative sum
g = (data.groupby('user_id')['event_timestamp'].diff() > pd.Timedelta('30Min')).cumsum()
#create counter of groups
data['session_id'] = data.groupby(['user_id', g], sort=False).ngroup() + 1





# Сбрасываем дубликаты действий внутри сессий

# In[31]:


data_clean=data.drop_duplicates(subset=['event_name','session_id'])
data_clean



# In[32]:


session_data=data_clean.groupby('event_name').agg({'session_id': 'nunique'}).sort_values(
    by='session_id', ascending=False).reset_index()
session_data
ax=session_data
plt.figure(figsize=(15, 8))
sns.barplot(x='session_id', y='event_name', data=ax)
sns.set_palette('muted')
plt.title('Распределение кол-во событий по отфильтрованным данным')
plt.xlabel('Количество событий')
plt.ylabel('События')
plt.xticks(rotation = 90)
plt.show()


# In[33]:


session_data


# Теперь отфильровав по сессиям и убрав дубликаты внутри сессии видим, что самым распространенным действием является tips_show, а наименее favorites_add, tips_click, contacts_call.  
# Стоит обратить внимание на большой разрыв между tips_show и tips_click, что очень маленький процент людей нажимает на рекомендованное объявление, необходимо изучить этот вопрос

# Общий вывод по шагу. 
# - Построив таблицу с распределением логов видим, что самый распространенный лог это tips_show (увидел рекомендованные объявления), затем просмотр фото и search. А самый менее распространенный лог это tips_click and contact_call. Целевое событие расположилось 5-м с конца 
# - На таблице самых активный пользователей Видим, что самый активный пользователь около топ15 активных пользвателей совершили примерно от 250 до 500 действий
# - Посмотрев данные через функцию describe() мы вилим, что в среднем пользователь соверашает 17 действий, а медианное значение говорит,что 9 действий. Минимальное количество действий это 1
# - Проверив по количеству пользователей и примененым действиям видим, что активность пользователей сильно меньше была 12 октября и также сильны провал в активности наблюдался в 2 ноября. Проверив календарь, видим, что оба дня были субботами. Надо преврить активность по дням недели. 
# -  в графике по дням неделям Видим заметное проседание в активности во второй половине недели, в особенности в субботу.
# - Подсчитали сессий, создали колонку session_id и построили воронку событий.   
# видим, что самым распространенным действием является tips_show, а наименее favorites_add, tips_click, contacts_call.  
# Стоит обратить внимание на большой разрыв между tips_show и tips_click, что очень маленький процент людей нажимает на рекомендованное объявление, необходимо изучить этот вопрос

# ## Анализ связи целевого события с другими событиями

# ### Диаграмма Санкея

# Строим диаграмму санкеяю. 
# Создаем новые функции для диаграмму и применем новые отфильтрованную по сессиям таблицу 

# In[34]:


def add_features(df):
    
    """Функция генерации новых столбцов для исходной таблицы

    Args:
        df (pd.DataFrame): исходная таблица.
    Returns:
        pd.DataFrame: таблица с новыми признаками.
    """
    
    # сортируем по id и времени
    sorted_df = df.sort_values(by=['session_id', 'event_timestamp']).copy()
    # добавляем шаги событий
    sorted_df['step'] = sorted_df.groupby('session_id').cumcount() + 1
    
    # добавляем узлы-источники и целевые узлы
    # узлы-источники - это сами события
    sorted_df['source'] = sorted_df['event_name']
    # добавляем целевые узлы
    sorted_df['target'] = sorted_df.groupby('session_id')['source'].shift(-1)
    
    # возврат таблицы без имени событий
    return sorted_df.drop(['event_name'], axis=1)
  
# преобразуем таблицу
table = add_features(data_clean)
table


# In[35]:


def get_source_index(df):
    
    """Функция генерации индексов source

    Args:
        df (pd.DataFrame): исходная таблица с признаками step, source, target.
    Returns:
        dict: словарь с индексами, именами и соответсвиями индексов именам source.
    """
    
    res_dict = {}
    
    count = 0
    # получаем индексы источников
    for no, step in enumerate(df['step'].unique().tolist()):
        # получаем уникальные наименования для шага
        res_dict[no+1] = {}
        res_dict[no+1]['sources'] = df[df['step'] == step]['source'].unique().tolist()
        res_dict[no+1]['sources_index'] = []
        for i in range(len(res_dict[no+1]['sources'])):
            res_dict[no+1]['sources_index'].append(count)
            count += 1
            
    # соединим списки
    for key in res_dict:
        res_dict[key]['sources_dict'] = {}
        for name, no in zip(res_dict[key]['sources'], res_dict[key]['sources_index']):
            res_dict[key]['sources_dict'][name] = no
    return res_dict
  

# создаем словарь
source_indexes = get_source_index(table)


# In[36]:


def colors_for_sources(mode):
    
    """Генерация цветов rgba

    Args:
        mode (str): сгенерировать случайные цвета, если 'random', а если 'custom' - 
                    использовать заранее подготовленные
    Returns:
        dict: словарь с цветами, соответствующими каждому индексу
    """
    # словарь, в который сложим цвета в соответствии с индексом
    colors_dict = {}
    
    if mode == 'random':
        # генерим случайные цвета
        for label in table['source'].unique():
            r, g, b = np.random.randint(255, size=3)            
            colors_dict[label] = f'rgba({r}, {g}, {b}, 1)'
            
    elif mode == 'custom':
        # присваиваем ранее подготовленные цвета
        colors = requests.get('https://raw.githubusercontent.com/rusantsovsv/senkey_tutorial/main/json/colors_senkey.json').json()
        for no, label in enumerate(table['source'].unique()):
            colors_dict[label] = colors['custom_colors'][no]
            
    return colors_dict
  
  
# генерю цвета из своего списка
colors_dict = colors_for_sources(mode='custom')


# In[37]:


def percent_users(sources, targets, values):
    
    """
    Расчет уникальных id в процентах (для вывода в hover text каждого узла)
    
    Args:
        sources (list): список с индексами source.
        targets (list): список с индексами target.
        values (list): список с "объемами" потоков.
        
    Returns:
        list: список с "объемами" потоков в процентах
    """
    
    # объединим источники и метки и найдем пары
    zip_lists = list(zip(sources, targets, values))
    
    new_list = []
    
    # подготовим список словарь с общим объемом трафика в узлах
    unique_dict = {}
    
    # проходим по каждому узлу
    for source, target, value in zip_lists:
        if source not in unique_dict:
            # находим все источники и считаем общий трафик
            unique_dict[source] = 0
            for sr, tg, vl in zip_lists:
                if sr == source:
                    unique_dict[source] += vl
                    
    # считаем проценты
    for source, target, value in zip_lists:
        new_list.append(round(100 * value / unique_dict[source], 1))
    
    return new_list


# In[38]:


def lists_for_plot(source_indexes=source_indexes, colors=colors_dict, frac=10):
    
    """
    Создаем необходимые для отрисовки диаграммы переменные списков и возвращаем
    их в виде словаря
    
    Args:
        source_indexes (dict): словарь с именами и индексами source.
        colors (dict): словарь с цветами source.
        frac (int): ограничение на минимальный "объем" между узлами.
        
    Returns:
        dict: словарь со списками, необходимыми для диаграммы.
    """
    
    sources = []
    targets = []
    values = []
    labels = []
    link_color = []
    link_text = []

    # проходим по каждому шагу
    for step in tqdm(sorted(table['step'].unique()), desc='Шаг'):
        if step + 1 not in source_indexes:
            continue

        # получаем индекс источника
        temp_dict_source = source_indexes[step]['sources_dict']

        # получаем индексы цели
        temp_dict_target = source_indexes[step+1]['sources_dict']

        # проходим по каждой возможной паре, считаем количество таких пар
        for source, index_source in tqdm(temp_dict_source.items()):
            for target, index_target in temp_dict_target.items():
                # делаем срез данных и считаем количество id            
                temp_df = table[(table['step'] == step)&(table['source'] == source)&(table['target'] == target)]
                value = len(temp_df)
                # проверяем минимальный объем потока и добавляем нужные данные
                if value > frac:
                    sources.append(index_source)
                    targets.append(index_target)
                    values.append(value)
                    # делаем поток прозрачным для лучшего отображения
                    link_color.append(colors[source].replace(', 1)', ', 0.2)'))
                    
    labels = []
    colors_labels = []
    for key in source_indexes:
        for name in source_indexes[key]['sources']:
            labels.append(name)
            colors_labels.append(colors[name])
            
    # посчитаем проценты всех потоков
    perc_values = percent_users(sources, targets, values)
    
    # добавим значения процентов для howertext
    link_text = []
    for perc in perc_values:
        link_text.append(f"{perc}%")
    
    # возвратим словарь с вложенными списками
    return {'sources': sources, 
            'targets': targets, 
            'values': values, 
            'labels': labels, 
            'colors_labels': colors_labels, 
            'link_color': link_color, 
            'link_text': link_text}
  

# создаем словарь
data_for_plot = lists_for_plot()


# In[39]:


def plot_senkey_diagram(data_dict=data_for_plot):    
    
    """
    Функция для генерации объекта диаграммы Сенкей 
    
    Args:
        data_dict (dict): словарь со списками данных для построения.
        
    Returns:
        plotly.graph_objs._figure.Figure: объект изображения.
    """
    
    fig = go.Figure(data=[go.Sankey(
        domain = dict(
          x =  [0,1],
          y =  [0,1]
        ),
        orientation = "h",
        valueformat = ".0f",
        
        node = dict(
          pad = 50,
          thickness = 15,
          line = dict(color = "black", width = 0.1),
          label = data_dict['labels'],
          color = data_dict['colors_labels']
        ),
        link = dict(
          source = data_dict['sources'],
          target = data_dict['targets'],
          value = data_dict['values'],
          label = data_dict['link_text'],
          color = data_dict['link_color']
      ))])
    fig.update_layout(title_text="Sankey Diagram", font_size=10, width=1000, height=500)

   


    
    # возвращаем объект диаграммы
    return fig
  

# сохраняем диаграмму в переменную
senkey_diagram = plot_senkey_diagram()


# In[40]:


senkey_diagram.show()



# 1. Видим что количество шагов всех сессий ограничивается 4 шагами максимум
# 2. Самые популярные первые шаги tips_show, map, search
# 3. Что в основном tips_show, photos_show, search до целевого события contact_show доходят за 1 шаг

# ### Строим воронки сценариев

# #### Воронка map - contacts_show



# In[41]:


map_data=  data_clean.query('event_name == "map" ')
map_data_line=map_data.groupby('event_name')['user_id'].nunique().reset_index()
map_data_line=map_data_line[map_data_line['event_name']=='map']
map_data_line


# In[42]:



map_data_users=map_data.query('event_name =="map"')['user_id'].unique().tolist()


# In[43]:



contacts_map= data_clean.query('user_id == @map_data_users and event_name == "contacts_show" ')

contacts_map_line=contacts_map.groupby('event_name')['user_id'].nunique().reset_index()
contacts_map_line=contacts_map_line[contacts_map_line['event_name']=='contacts_show']


# In[44]:



comb_data_user=map_data_line.append(contacts_map_line)
comb_data_user


# In[45]:


contacts_map_count = comb_data_user['user_id'].to_list()
contacts_map_name  = comb_data_user['event_name'].to_list()


fig = go.Figure()
fig.add_trace(go.Funnel(
    y =contacts_map_name,
    x = contacts_map_count,
    textposition = "auto",
    textinfo = "value+percent initial+percent previous"

))
fig.update_layout(title='Воронка конверсии пользователей map contacts_show')
fig.show()


# #### Строим воронку search photos_show contacts_show

# Строим сценарий пользователя который уже знает, что ему нужно и ищет через поиск. search photos_show contacts_show

# In[46]:


search_data=  data_clean.query('event_name == "search" ')
search_data_line=search_data.groupby('event_name')['user_id'].nunique().reset_index()
search_data_line=search_data_line[search_data_line['event_name']=='search']


search_data_users=search_data.query('event_name =="search"')['user_id'].unique().tolist()

search_show= data_clean.query('user_id == @search_data_users and event_name == "photos_show" ')


search_show_line=search_show.groupby('event_name')['user_id'].nunique().reset_index()
search_show_line_1=search_show_line[search_show_line['event_name']=='photos_show']

comb_data_user=search_data_line.append(search_show_line)


search_show_users=search_show['user_id'].unique().tolist()




search_show_contacts= data_clean.query('user_id == @search_show_users and event_name == "contacts_show" ')


search_show_contacts_line=search_show_contacts.groupby('event_name')['user_id'].nunique().reset_index()
search_show_contacts_line=search_show_contacts_line[search_show_contacts_line['event_name']=='contacts_show']

comb_data_user=comb_data_user.append(search_show_contacts_line)

search_show_contacts_count = comb_data_user['user_id'].to_list()
search_show_contacts_name  = comb_data_user['event_name'].to_list()


fig = go.Figure()
fig.add_trace(go.Funnel(
    y =search_show_contacts_name ,
    x = search_show_contacts_count,
    textposition = "auto",
    textinfo = "value+percent initial+percent previous"

))
fig.update_layout(title='Воронка конверсии пользователей map contacts_show')
fig.show()


# Конвертация с search- photos_show почти 39%, и 12% до целевого события.   
# То есть конвертация в ЦС для пользователя, который пришел в пришел зная что ему надо, поиск и показ фото работает хорошо.

# #### Воронка tips_show-contacts_show-tips_click

# Разберем как работает функция рекомендаций объявлений, построим как часто люди нажимают на рекомендованные объявления и как часто потом смотрит contacts_show

# In[ ]:





# In[47]:


#1ряд и 2ряд
contacts_photo=  data.query('event_name == "tips_show" or event_name == "contacts_show" or event_name == "tips_click" ')
contacts_photo_count = contacts_photo.groupby('event_name')['user_id'].nunique().sort_values(
    ascending=False).reset_index()['user_id'].to_list()
contacts_photo_name = contacts_photo.groupby('event_name')['user_id'].nunique().sort_values(
    ascending=False).reset_index()['event_name'].to_list()


tips_show_data=  data_clean.query('event_name == "tips_show" ')
tips_show_line=tips_show_data.groupby('event_name')['user_id'].nunique().reset_index()
tips_show_line=tips_show_line[tips_show_line['event_name']=='tips_show']


tips_show_users=tips_show_data.query('event_name =="tips_show"')['user_id'].unique().tolist()

tips_show_contacts= data_clean.query('user_id == @tips_show_users and event_name == "contacts_show" ')


tips_show_contacts_line=tips_show_contacts.groupby('event_name')['user_id'].nunique().reset_index()
tips_show_contacts_line=tips_show_contacts_line[tips_show_contacts_line['event_name']=='contacts_show']

comb_data_user=tips_show_line.append(tips_show_contacts_line)

#3ряд

tips_show_contacts_users=tips_show_contacts['user_id'].unique().tolist()
tips_show_contacts_click= data_clean.query('user_id == @tips_show_contacts_users and event_name == "tips_click" ')


tips_show_contacts_click_line=tips_show_contacts_click.groupby('event_name')['user_id'].nunique().reset_index()


comb_data_user=comb_data_user.append(tips_show_contacts_click_line)

tips_show_contacts_click_count = comb_data_user['user_id'].to_list()
tips_show_contacts_click_name  = comb_data_user['event_name'].to_list()



fig = go.Figure()
fig.add_trace(go.Funnel(
    y = tips_show_contacts_click_name,
    x = tips_show_contacts_click_count,
    textposition = "auto",
    textinfo = "value+percent initial+percent previous"
))
fig.update_layout(title='Воронка конверсии tips_show-contacts_show-tips_click')
fig.show()


# Видим что лишь 3 процента пользователей нажимает на рекомендованные объявления, что даже меньше чем ЦС на 18%  
# Возможно необхдимо изучить проблемы в функции подборки рекомендации

# Обший вывод по шагу  
#   - Построили Диаграмму санкея и увидели следующее:
#     1. Видим что количество шагов всех сессий ограничивается 4 шагами максимум
#     2. Самые популярные первые шаги tips_show, map, search
#     3. Что в основном tips_show, photos_show, search до целевого события contact_show доходят за 1 шаг
# - Строим воронку из трех самых первых шагов с Целевым событием с tips_show search  map contacts_show
#     1. Видим что почти 20% процентов переходят на открытия контактных данных, после осмотра карты. Говорит о умеренном функционале карты
# - Строим сценарий пользователя который уже знает, что ему нужно и ищет через поиск search photos_show contacts_show
#     1.Конвертация с search- photos_show почти 39%, и 12% до целевого события.   То есть конвертация в ЦС для пользователя, который пришел в пришел зная что ему надо, поиск и показ фото работает хорошо.
# -  Воронка tips_show-contacts_show-tips_click Разберем как работает функция рекомендаций объявлений, построим как часто люди нажимают на рекомендованные объявления и как часто потом смотрит contacts_show
#     1. Видим что лишь 3 процента пользователей нажимает на рекомендованные объявления, что даже меньше чем ЦС на 18%  
# Возможно необхдимо изучить проблемы в функции подборки рекомендации

# ## Частота событий в разрезе двух групп пользователей. (смотрели/не смотрели contacts_show)

# Рассчитаем и построим график по этим двум группам

# Пользователей которые посмотрели карточки

# In[48]:


watched_users=data.query('event_name=="contacts_show"')
watched_users_list=watched_users['user_id'].unique().tolist()
print('Количество пользователей которые посмотрели карточки', watched_users['user_id'].nunique())



# 

# <div class="alert alert-success" style="border-radius: 15px; box-shadow: 4px 4px 4px; border: 1px solid; position: relative; padding: 15px; padding-left: 80px;">
# <img src="https://lh3.googleusercontent.com/a/AAcHTtc31jlywy-FMYxLAouSSqNAmm5NsrBvivwRIASNt7wihI2ClYdpAbzWNqcigfcR04LfvopHwsJrJpnVr4UXDkCHtWk=s432-c-no" width="45" height="45" style="position: absolute; top: 15px; left: 15px; border-radius: 50%;">
# <b> ✔️ Комментарий тимлида [v2] : </b>
# 
# 👍
# 
# </div>

# Пользователей которые не посмотрели карточки

# In[49]:


not_watched_users=list(set(data['user_id'].unique())-set(watched_users_list))
not_watched_users_list=data.query('user_id == @not_watched_users')['user_id'].unique().tolist()
print('Количество пользователей которые не посмотрели карточки',data.query(
    'user_id == @not_watched_users')['user_id'].nunique())




# In[50]:


watched_data=data.query('user_id==@watched_users_list')


# In[51]:


watched_data_list=watched_data['event_name'].value_counts().reset_index()

watched_data_list['%']=100*watched_data_list['event_name']/watched_data_list['event_name'].sum()
watched_data_list.columns=['event_name', 'watched_count','%watched']
watched_data_list


# In[52]:


not_watched_data=data.query('user_id==@not_watched_users_list')


# In[53]:


not_watched_data_list=not_watched_data['event_name'].value_counts().reset_index()
not_watched_data_list['%']=100*not_watched_data_list['event_name']/not_watched_data_list['event_name'].sum()
not_watched_data_list.columns=['event_name', 'not_watched_count','%not_watched']
not_watched_data_list


# In[54]:


data_comb=watched_data_list.merge(not_watched_data_list, on='event_name', how='left')
data_comb.fillna(0)









# Частота событий в разрезе двух групп пользователей. (смотрели/не смотрели contacts_show)¶
# Рассчитаем и построим график по этим двум группам
# 
# - Количество пользователей которые посмотрели карточки 981
# - Количество пользователей которые не посмотрели карточки 3312  
# 
# Только доля  watched действия photo_show превышает долю от not_watched того же действия   
# Доля остальных действий выше в группе непосмотревших контакты, чем в группе смотревших

# ## Статистический анализ данных

# ### a. Одни пользователи совершают действия tips_show и tips_click , другие —только tips_show . Проверьте гипотезу: конверсия в просмотры контактов различается у этих двух групп.
# 

# Считаем количествово посмотревших tips_show и tips_click пользователей и конверсию

# 1. Количествово tips_show и tips_click пользователей

# In[55]:


tips_users = data.query('event_name =="tips_show"')['user_id'].unique().tolist()
tips_click_users = data.query('event_name =="tips_click" and user_id==@tips_users'
                             )['user_id'].unique().tolist()

tips_click_count = data.query('user_id==@tips_click_users')[['user_id', 'event_name']]

tips_click_count


# In[56]:


tips_click_count_len=tips_click_count['user_id'].nunique()
print('Количествово tips_show и tips_click пользователей: ', tips_click_count_len)


# In[57]:


tips_click_count_goal_event=tips_click_count[
    tips_click_count['event_name']=="contacts_show"]['user_id'].nunique()

print('Количествово пользователей с целевым событием и tips_show+click:', tips_click_count_goal_event)


# In[58]:


tips_click_conv = tips_click_count_goal_event/tips_click_count_len
print(f'Конверсия tips_show+click пользователей = {round(tips_click_conv*100, 2)}%')


# 2. Количествово только tips_show пользователей:

# In[59]:


only_tips_users = list(set(tips_users) - set(tips_click_users))
only_tips_users_list=data.query('user_id==@only_tips_users')['user_id'].unique().tolist()
tips_click_count = data.query('user_id==@tips_click_users')[['user_id', 'event_name']]


# In[60]:


only_tips_users_data = data.query('user_id==@only_tips_users_list')[['user_id', 'event_name']]
only_tips_users_data 


# In[61]:


show_events_len=only_tips_users_data['user_id'].nunique()
print('Количествово только tips_show пользователей:', show_events_len)


# In[62]:


only_tips_users_list_goal_event=only_tips_users_data[
    only_tips_users_data['event_name']=="contacts_show"]['user_id'].nunique()

print('Количествово только tips_show с целевым событием пользователей:', only_tips_users_list_goal_event)


# In[63]:


tips_show_conv=only_tips_users_list_goal_event/show_events_len
print(f'Конверсия только tips_show пользователей: {round(tips_show_conv*100, 2)}%')





# Гипотеза

# 
#   
#     H0 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click равна конверсии в просмотры группы пользователей совершающие только tips_show  
#     H1 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры группы пользователей совершающие только tips_show

# <div class="alert alert-success" style="border-radius: 15px; box-shadow: 4px 4px 4px; border: 1px solid; position: relative; padding: 15px; padding-left: 80px;">
# <img src="https://lh3.googleusercontent.com/a/AAcHTtc31jlywy-FMYxLAouSSqNAmm5NsrBvivwRIASNt7wihI2ClYdpAbzWNqcigfcR04LfvopHwsJrJpnVr4UXDkCHtWk=s432-c-no" width="45" height="45" style="position: absolute; top: 15px; left: 15px; border-radius: 50%;">
# <b> ✔️ Комментарий тимлида [v2] : </b>
# 
# Очень хорошо, что не забываешь про формулировку гипотез. Это важный пункт в подобного рода задачах.
# 
# </div>

# Делаем z-test так как перед нами сравнение между двумя зависимыми группами чей размер нам извстен

# In[64]:


def z_test(successes, trials, alpha): 
    
    # пропорция успехов в первой группе:
    p1 = successes[0]/trials[0]

    # пропорция успехов во второй группе:
    p2 = successes[1]/trials[1]

    # пропорция успехов в комбинированном датасете:
    p_combined = (successes[0] + successes[1]) / (trials[0] + trials[1])

    # разница пропорций в датасетах
    difference = p1 - p2 

    # считаем статистику в ст.отклонениях стандартного нормального распределения
    z_value = difference / mth.sqrt(p_combined * (1 - p_combined) * (1/trials[0] + 1/trials[1]))

    # задаем стандартное нормальное распределение (среднее 0, ст.отклонение 1)
    distr = st.norm(0, 1)

    p_value = (1 - distr.cdf(abs(z_value))) * 2

    print('p-значение: ', p_value)

    if p_value < alpha:
        print('Отвергаем нулевую гипотезу: между долями есть значимая разница')
    else:
        print(
            'Не получилось отвергнуть нулевую гипотезу, нет оснований считать доли разными'
        ) 


# In[65]:


alpha = .05
successes = [tips_click_count_goal_event, only_tips_users_list_goal_event]
trials = [tips_click_count_len, show_events_len]
z_test(successes, trials, alpha) 




# По итогам z-test мы отвергаем нулевую гипотезу.  
# 
# Вывод: конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры группы пользователей совершающие только tips_show

# ### b. Конверсия в просмотры группы пользователей  воспользовавшихся функцией map больше, чем у группы пользователей, которые не пользовались ей.
# 
# 

# 1. Количествово map пользователей

# In[66]:


map_users = data.query('event_name =="map"')['user_id'].unique().tolist()


map_users_count = data.query('user_id==@map_users')[['user_id', 'event_name']]


# In[67]:


map_count=map_users_count['user_id'].nunique()
print('Количествово событий у map пользователей: ', map_count)


# In[68]:


goal_event_map=map_users_count[map_users_count['event_name']=="contacts_show"]['user_id'].nunique()
print('Количествово целевого события у map пользователей =', goal_event_map)


# In[69]:


map_conv = goal_event_map / map_count
print(f'Конверсия map пользователей = {round(map_conv *100, 2)}%')


# 2. Количествово no_map пользователей

# In[70]:


no_map_users = list(set(data['user_id'].unique().tolist()) - set(map_users))
no_map_user_counts = data.query('user_id==@no_map_users')[['user_id', 'event_name']]
goal_event_no_map=no_map_user_counts[
    no_map_user_counts['event_name']=="contacts_show"]['user_id'].nunique()
no_map_count=no_map_user_counts['user_id'].nunique()


# In[71]:


print('Количествово no_map пользователей:', no_map_count)


# In[72]:


print('Количествово no_map пользователей:', goal_event_no_map)


# In[73]:


no_map_conv=goal_event_no_map/no_map_count
print(f'Конверсия в целевого события no_map пользователей = {round(no_map_conv*100, 2)}%')


# Гипотеза 

#  
#         H0 - конверсия в просмотры группы пользователей совершающие действие map равна конверсии в просмотры группы пользователей, которые это действие не совершили  
#         H1 - конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили

# In[74]:


alpha = .05
successes = [goal_event_map, goal_event_no_map]
trials = [map_count, no_map_count]
z_test(successes, trials, alpha) 




# По итогам z-test мы отвергаем нулевую гипотезу. Вывод: конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили
# 

# Общий вывод по шагу.   
# 
# Одни пользователи совершают действия tips_show и tips_click , другие —только tips_show . Проверьте гипотезу: конверсия в просмотры контактов различается у этих двух групп.  
# 
# Данные по группе с tips_show и tips_click
# - Количествово событий у tips_show и tips_click пользователей: 297
# - Количествово целевого события у tips_show+click пользователей: 91  
# - Конверсия tips_show+click пользователей = 6.83%
# 
# Данные по группе только tips_show
# 
# - Количествово событий только tips_show пользователей: 2504
# - Количествово целевого события у только tips_show пользователей: 425
# - Конверсия в целевого события у только tips_show пользователей = 30.64%  
# 
# 
# Гипотеза
# 
#     H0 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click равна конверсии в просмотры группы пользователей совершающие только tips_show  
#     H1 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры группы пользователей совершающие только tips_show
#     Делаем z-test так как перед нами сравнение между двумя зависимыми группами чей размер нам извстен
#     
#         p-значение:  9.218316554537864e-09
#         Отвергаем нулевую гипотезу: между долями есть значимая разница
#         alpha = .05
#     По итогам z-test мы отвергаем нулевую гипотезу. Вывод: конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры группы пользователей совершающие только tips_show
#     
# b. Конверсия в просмотры группы пользователей воспользовавшихся функцией map больше, чем у группы пользователей, которые не пользовались ей.
# 
# - Количествово событий у map пользователей:  1456
# - Количествово целевого события у map пользователей = 289
# - Конверсия map пользователей = 30.64%
# 
# - Количествово событий у no_map пользователей: 2837
# - Количествово целевого события у no_map пользователей: 692
# - Конверсия в целевого события no_map пользователей = 24.39%
# 
# Гипотеза
# 
#     H0 - конверсия в просмотры группы пользователей совершающие действие map равна конверсии в просмотры группы пользователей, которые это действие не совершили  
#     H1 - конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили
# 
#         alpha = .05
#         z_test(successes, trials, alpha) 
#         p-значение:  0.0007899493753891207
#     По итогам z-test мы отвергаем нулевую гипотезу. Вывод: конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили

# ## Общий вывод

# 1  Описание данных:
# Описание данных: Датасет содержит данные о событиях, совершенных в мобильном приложении "Ненужные вещи". В нем пользователи продают свои ненужные вещи, размещая их на доске объявлений.
# 
#   
#   В датасете содержатся данные пользователей, впервые совершивших действия в приложении после 7 октября 2019 года.
# Колонки в /datasets/mobile_sources.csv :  
# 
# userId — идентификатор пользователя,  
# 
# source — источник, с которого пользователь установил приложение.  
# 
# Колонки в /datasets/mobile_dataset.csv :  
# 
# event.time — время совершения,  
# 
# user.id — идентификатор пользователя,  
# 
# event.name — действие пользователя.  
# 
# Виды действий:  
# 
# advert_open — открыл карточки объявления,  
# 
# photos_show — просмотрел фотографий в объявлении,  
# 
# tips_show — увидел рекомендованные объявления,  
# 
# tips_click — кликнул по рекомендованному объявлению,  
# 
# contacts_show и show_contacts — посмотрел номер телефона,  
# 
# contacts_call — позвонил по номеру из объявления,  
# 
# map — открыл карту объявлений, 
# 
# search_1 — search_7 — разные действия, связанные с поиском по сайту,  
# 
# favorites_add — добавил объявление в избранное.    
# 
# 
# 2 Шаг Импорт библиотек. Предобработка данных.
#   
# - Проверили на пропуски и дубпликаты. ничего не нашли  
# - Переименовали столбцы. 
# - Объединили значения contacts_show и show_contacts
# - Объединили  'search_1', 'search_2', 'search_3', 'search_4', 'search_5', 'search_6', 'search_7', в один лог search
# - привели столбец с датами к нужному формату  
# 
# 3 Шаг  Исследуем данные
# 
# - Построив таблицу с распределением логов видим, что самый распространенный лог это tips_show (увидел рекомендованные объявления), затем просмотр фото и search. А самый менее распространенный лог это tips_click and contact_call. Целевое событие расположилось 5-м с конца 
# - На таблице самых активный пользователей Видим, что самый активный пользователь около топ15 активных пользвателей совершили примерно от 250 до 500 действий
# - Посмотрев данные через функцию describe() мы вилим, что в среднем пользователь соверашает 17 действий, а медианное значение говорит,что 9 действий. Минимальное количество действий это 1
# - Проверив по количеству пользователей и примененым действиям видим, что активность пользователей сильно меньше была 12 октября и также сильны провал в активности наблюдался в 2 ноября. Проверив календарь, видим, что оба дня были субботами. Надо преврить активность по дням недели. 
# -  в графике по дням неделям Видим заметное проседание в активности во второй половине недели, в особенности в субботу.
# - Подсчитали сессий, создали колонку session_id и построили воронку событий.   
# видим, что самым распространенным действием является tips_show, а наименее favorites_add, tips_click, contacts_call.  
# Стоит обратить внимание на большой разрыв между tips_show и tips_click, что очень маленький процент людей нажимает на рекомендованное объявление, необходимо изучить этот вопрос
# 
# 4 Шаг. Анализ связи целевого события с другими событиями
#  
#   - Построили Диаграмму санкея и увидели следующее:
#     1. Видим что количество шагов всех сессий ограничивается 4 шагами максимум
#     2. Самые популярные первые шаги tips_show, map, search
#     3. Что в основном tips_show, photos_show, search до целевого события contact_show доходят за 1 шаг
# - Строим воронку из трех самых первых шагов с Целевым событием с tips_show search  map contacts_show
#     1. Видим что почти 20% процентов переходят на открытия контактных данных, после осмотра карты. Говорит о умеренном функционале карты
# - Строим сценарий пользователя который уже знает, что ему нужно и ищет через поиск search photos_show contacts_show
#     1.Конвертация с search- photos_show почти 39%, и 12% до целевого события.   То есть конвертация в ЦС для пользователя, который пришел в пришел зная что ему надо, поиск и показ фото работает хорошо.
# -  Воронка tips_show-contacts_show-tips_click Разберем как работает функция рекомендаций объявлений, построим как часто люди нажимают на рекомендованные объявления и как часто потом смотрит contacts_show
#     1. Видим что лишь 3 процента пользователей нажимает на рекомендованные объявления, что даже меньше чем ЦС на 18%  
# Возможно необхдимо изучить проблемы в функции подборки рекомендации
#       
#       
#   
# 5 Шаг. Частота событий в разрезе двух групп пользователей. (смотрели/не смотрели contacts_show)
#  Частота событий в разрезе двух групп пользователей. (смотрели/не смотрели contacts_show)¶
# Рассчитаем и построим график по этим двум группам
# 
# - Количество пользователей которые посмотрели карточки 4529
# - Количество пользователей которые не посмотрели карточки 69668
# 
#   
#   Только доля  watched действия photo_show превышает долю от not_watched того же действия 
#   Доля остальных действий выше в группе непосмотревших контакты, чем в группе смотревших
#   
#   
# 6 Шаг. 
#  
# 
# Одни пользователи совершают действия tips_show и tips_click , другие —только tips_show . Проверьте гипотезу: конверсия в просмотры контактов различается у этих двух групп.  
# 
# Данные по группе с tips_show и tips_click
# 
# - Количествово событий у tips_show и tips_click пользователей: 297
# - Количествово целевого события у tips_show+click пользователей: 91  
# - Конверсия tips_show+click пользователей = 30.64%
# 
# Данные по группе только tips_show
# 
# - Количествово событий только tips_show пользователей: 2504
# - Количествово целевого события у только tips_show пользователей: 425
# - Конверсия в целевого события у только tips_show пользователей = 16.97%
# 
# 
# Гипотеза
# 
#     H0 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click равна конверсии в просмотры группы пользователей совершающие только tips_show  
#     H1 - конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры группы пользователей совершающие только tips_show
#     Делаем z-test так как перед нами сравнение между двумя зависимыми группами чей размер нам извстен
#     
#         p-значение:  9.218316554537864e-09
#         Отвергаем нулевую гипотезу: между долями есть значимая разница
#         alpha = .05
#     По итогам z-test мы отвергаем нулевую гипотезу. Вывод: конверсия в просмотры группы пользователей совершающие действия tips_show и tips_click не равна конверсии в просмотры группы пользователей совершающие только tips_show
#     
# b. Конверсия в просмотры группы пользователей воспользовавшихся функцией map больше, чем у группы пользователей, которые не пользовались ей.
# 
# - Количествово событий у map пользователей:  1456
# - Количествово целевого события у map пользователей = 289
# - Конверсия map пользователей = 19.85%
#   
#   
# - Количествово событий у no_map пользователей: 2837
# - Количествово целевого события у no_map пользователей: 692
# - Конверсия в целевого события no_map пользователей = 24.39%
# 
# Гипотеза
# 
#     H0 - конверсия в просмотры группы пользователей совершающие действие map равна конверсии в просмотры группы пользователей, которые это действие не совершили  
#     H1 - конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили
# 
#         alpha = .05
#         z_test(successes, trials, alpha) 
#         p-значение:  0.0007899493753891207
#         Отвергаем нулевую гипотезу: между долями есть значимая разница
#     По итогам z-test мы отвергаем нулевую гипотезу. Вывод: конверсия в просмотры группы пользователей совершающие действия map не равна конверсии в просмотры группы пользователей, которые это действие не совершили

# Рекомендации для бизнеса:  
# 
# - Изучить какие обстоятельства могли повлиять на активность и посещяемость пользователей в выходные дни, особенно субботу
# - Необходимо улучшить алгоритмы рекомендации карточек объявлений, чтобы увеличить конвертация пользователей с tips_show по tips_click, так как:   
#     a. Конверсия у группы группе только tips_show почти на 24 процента больше, чем tips_show+click (Z-тест показал, что данная разница не является статистической погрешностью)
#     b. также конверсия tips_show в tips_click составляет только 11 процентов
# 
# 

# <div id="div_id9" class="alert alert-danger" style="border-radius: 15px; box-shadow: 4px 4px 4px; border: 1px solid; position: relative; padding: 15px; padding-left: 80px;">
# <img src="https://lh3.googleusercontent.com/a/AAcHTtc31jlywy-FMYxLAouSSqNAmm5NsrBvivwRIASNt7wihI2ClYdpAbzWNqcigfcR04LfvopHwsJrJpnVr4UXDkCHtWk=s432-c-no" width="45" height="45" style="position: absolute; top: 15px; left: 15px; border-radius: 50%;">
# <b> НАПОМИНАНИЕ : </b>
# 
# 
# После того как ты внесёшь необходимые исправления замечаний, обязательно пересмотри и актуализируй итоговое заключение.
# 
# </div>
