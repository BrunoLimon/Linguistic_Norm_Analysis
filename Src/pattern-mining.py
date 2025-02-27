# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb

from matplotlib.ticker import AutoMinorLocator
from matplotlib import gridspec

#scaling, normalization
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

from sklearn import metrics


from google.colab import files

from mlxtend.preprocessing import TransactionEncoder

from mlxtend.frequent_patterns import association_rules


# %%
#caricamento del dataset
df = pd.read_csv('words_glasgow.csv')
#faccio una copia del dataset in caso di manipolazione dati
dfcopy= df.copy()

# %% [markdown]
# #Preprocess

# %%
df2 = df.copy()
#new variable 
df2["perceivability"] = df2[["imageability", "concreteness"]].mean(axis=1)

df_perc=df2.drop(["concreteness","imageability"], axis=1)

dfprepro= df_perc.copy()
#rename
dfprepro=dfprepro.rename(columns={"gender": "masculinity"})

df_missing=dfprepro.copy()

#dfprepro.loc[(dfprepro['web_corpus_freq'].isnull() == True), 'web_corpus_freq'] = dfprepro['web_corpus_freq'].mean()

#drop missing values
dfprepro=dfprepro.dropna()

dfprepro[dfprepro['web_corpus_freq'].isnull()]

dfprepro["web_corpus_log"] = pd.qcut(dfprepro["web_corpus_freq"], 10) 

#taglio la variabile web_corpus_freq in tot gruppi

dataframe = [dfprepro]

for dataset in dataframe:
    dataset.loc[(dataset["web_corpus_freq"] > 10000) & (dataset["web_corpus_freq"] <= 100000), "web_corpus_freq"] = 4
    dataset.loc[(dataset["web_corpus_freq"] > 100000) & (dataset["web_corpus_freq"] <= 1000000), "web_corpus_freq"] = 5
    dataset.loc[(dataset["web_corpus_freq"] > 1000000) & (dataset["web_corpus_freq"] <= 10000000), "web_corpus_freq"] = 6
    dataset.loc[(dataset["web_corpus_freq"] > 10000000) & (dataset["web_corpus_freq"] <= 100000000), "web_corpus_freq"] = 7
    dataset.loc[(dataset["web_corpus_freq"] > 100000000) & (dataset["web_corpus_freq"] <= 1000000000), "web_corpus_freq"] = 8
    dataset.loc[dataset["web_corpus_freq"] > 1000000000, "web_corpus_freq"] = 9
    
dfprepro = dfprepro.drop(["web_corpus_log","word"], axis=1)


#dfprepro.loc[(dfprepro['web_corpus_freq'].isnull() == True), 'web_corpus_freq'] = dfprepro['web_corpus_freq'].mean()
dfprepro.isnull().sum()

# %%
df_pm= dfprepro.copy()
#normalization and scaling
var_to_scale=['length','aoa',"arousal","valence","dominance","familiarity","semsize","masculinity","perceivability"]

features = df_pm[var_to_scale]
scaler = MinMaxScaler().fit(features.values)
features = scaler.transform(features.values)

#from 1 to 4
df_pm[var_to_scale] = 4*features
df_pm.head()
#round down
df_pm=df_pm.apply(np.floor)

df_pm['length'] = df_pm['length'].astype(str) + '_Lenght'
df_pm['arousal'] = df_pm['arousal'].astype(str) + '_Arousal'
df_pm['valence'] = df_pm['valence'].astype(str) + '_Valence'
df_pm['dominance'] = df_pm['dominance'].astype(str) + '_Dominance'
df_pm['familiarity'] = df_pm['familiarity'].astype(str) + '_Familiarity'
df_pm['aoa'] = df_pm['aoa'].astype(str) + '_Age_of_Acquisition'
df_pm['semsize'] = df_pm['semsize'].astype(str) + '_SemSize'
df_pm['masculinity'] = df_pm['masculinity'].astype(str) + '_Masculinity'
df_pm['web_corpus_freq'] = df_pm['web_corpus_freq'].astype(str) + '_Web_Corpus_Freq'
df_pm['perceivability'] = df_pm['perceivability'].astype(str) + '_Perceivability'


polysemy_dict = {0: 'Not Polysemy', 1: 'Polysemy'}
df_pm['polysemy'] = df_pm['polysemy'].map(polysemy_dict)

df_pm.head()

X = df_pm.values.tolist()
#create a dataframe without polysemy
df_no_pol=df_pm.drop('polysemy',axis=1)

X_no_pol = df_no_pol.values.tolist()

# %%
#preprocess for mlxtend
te=TransactionEncoder()

te_ary=te.fit(X_no_pol).transform(X_no_pol)

df3=pd.DataFrame(te_ary,columns=te.columns_)

df3.head()

# %% [markdown]
# # Frequent Itemsets

# %%
from mlxtend.frequent_patterns import apriori
frequent_itemsets = apriori(df3, min_support=0.065,use_colnames=True)

frequent_itemsets

# %% [markdown]
# # Association Rules

# %%
from mlxtend.frequent_patterns import apriori
frequent_itemsets = apriori(df3, min_support=0.065,use_colnames=True)
res = association_rules(frequent_itemsets, metric='confidence',min_threshold=0.75)
#export to dataframe
res1= res[['antecedents','consequents','support','confidence','lift']]
#cut at lift threshold
res2 = res1[res1['lift']>2.1]
#sort
df2=res2.sort_values(by =['consequents','lift'],ascending=(True,False),ignore_index=True )
#reindex
df2.index=df2.index+1
df2

# %% [markdown]
# #Algoritmo di Citraro

# %%
!pip install pyfim
from fim import apriori
#how number of itemsets change with different supports and closed, maximal or all
len_max_it = []
len_cl_it = []
len_all_it = []
for i in range(1, 9+1):
    max_itemsets = apriori(X_no_pol, target='m', supp=i, zmin=1)
    cl_itemsets = apriori(X_no_pol, target='c', supp=i, zmin=1)
    all_itemsets = apriori(X_no_pol, target='s', supp=i, zmin=1)
    len_max_it.append( len(max_itemsets)  )
    len_cl_it.append( len(cl_itemsets) )
    len_all_it.append( len(all_itemsets) )
    
plt.plot(len_max_it, label='maximal')
plt.plot(len_all_it, label='all')

plt.plot(len_cl_it, label='closed')
plt.legend(fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel('support (%)', fontsize=15)

plt.show()

# %%
!pip install pyfim
from fim import apriori
#how number of itemsets change with different zmin and closed, maximal or all

len_max_it = []
len_cl_it = []
len_all_it = []
for i in range(0, 6+1):
    max_itemsets = apriori(X_no_pol, target='m', supp=6, zmin=i)
    cl_itemsets = apriori(X_no_pol, target='c', supp=6, zmin=i)
    len_max_it.append( len(max_itemsets)  )
    len_cl_it.append( len(cl_itemsets) )

for i in range(0, 6+1):
    all_itemsets = apriori(X_no_pol, target='s', supp=6, zmin=i)
    len_all_it.append( len(all_itemsets) )

    
plt.plot(len_max_it, label='maximal')
plt.plot(len_all_it, label='all')
plt.plot(len_cl_it, label='closed')
plt.legend(fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel('#zmin', fontsize=15)

plt.show()

# %%
!pip install pyfim
from fim import apriori
rules = apriori(X_no_pol, target='r', supp=6.5, zmin=1, conf=75, report='aScl')
len(rules)
#export to dataframe
df4 = pd.DataFrame(rules, columns=['target','antecedent','supp','supp (%)','conf','lift'])
columns_titles = ['antecedent','target','lift','conf','supp (%)','supp']
#reindex columns for better reading
df4=df4.reindex(columns=columns_titles)
#cut at thresholds
df4=df4.loc[df4['lift']>1.6]
df4=df4.loc[df4['supp (%)']>6.5]
#sorting
df4=df4.sort_values(by =['target','lift'],ascending=False,ignore_index=True )
#reindex rows
df4.index=df4.index+1
df4

# %%
df4=df4.round(2)

print(df4.to_latex())

# %%
df_Familiarity=df4.loc[df4['target']=='3.0_Familiarity']
df_Familiarity

# %%


# %%
df_Valence=df4.loc[df4['target']=='2.0_Valence']
df_Valence

# %%
df_Dominance=df4.loc[df4['target']=='2.0_Dominance']
df_Dominance

# %% [markdown]
# ## Replacing missing values

# %%
df_only_missing=df_missing[df_missing['web_corpus_freq'].isnull()]
df_temp=df_only_missing.copy()

# %%
#scale (come sopra)
var_to_scale=['length','aoa',"arousal","valence","dominance","familiarity","semsize","masculinity","perceivability"]

features = df_only_missing[var_to_scale]
scaler = MinMaxScaler().fit(features.values)
features = scaler.transform(features.values)


df_only_missing[var_to_scale] = 4*features
df_only_missing.head()

df_only_missing=df_only_missing[var_to_scale].apply(np.floor)

#df_only_missing=df_only_missing.drop(labels='web_corpus_freq',axis=1)

df_only_missing['length'] = df_only_missing['length'].astype(str) + '_Lenght'
df_only_missing['arousal'] = df_only_missing['arousal'].astype(str) + '_Arousal'
df_only_missing['valence'] = df_only_missing['valence'].astype(str) + '_Valence'
df_only_missing['dominance'] = df_only_missing['dominance'].astype(str) + '_Dominance'
df_only_missing['familiarity'] = df_only_missing['familiarity'].astype(str) + '_Familiarity'
df_only_missing['aoa'] = df_only_missing['aoa'].astype(str) + '_Age_of_Acquisition'
df_only_missing['semsize'] = df_only_missing['semsize'].astype(str) + '_SemSize'
df_only_missing['masculinity'] = df_only_missing['masculinity'].astype(str) + '_Masculinity'
#df_only_missing['web_corpus_freq'] = df_only_missing['web_corpus_freq'].astype(str) + '_Web_Corpus_Freq'
df_only_missing['perceivability'] = df_only_missing['perceivability'].astype(str) + '_Perceivability'

#you need to know wich word you are working with
df_only_missing['word'] = df_temp['word']


X_miss = df_only_missing.values.tolist()


# %%
rules = apriori(X_no_pol, target='r', supp=4, zmin=2, conf=60, report='aScl')

#export found rules to dataframe
df4 = pd.DataFrame(rules, columns=['target','antecedents','supp','supp (%)','conf','lift'])
#reindex columns
columns_titles = ['antecedents','target','lift','conf','supp (%)','supp']
df4=df4.reindex(columns=columns_titles)
#cuts
df4=df4.loc[df4['supp (%)']>2]

#which one are Web Coprus Freq?
df_web4=df4.loc[(df4['target']=='4.0_Web_Corpus_Freq')] 
df_web5=df4.loc[(df4['target']=='5.0_Web_Corpus_Freq')] 
df_web6=df4.loc[(df4['target']=='6.0_Web_Corpus_Freq')] 
df_web7=df4.loc[(df4['target']=='7.0_Web_Corpus_Freq')] 
df_web8=df4.loc[(df4['target']=='8.0_Web_Corpus_Freq')] 
df_web9=df4.loc[(df4['target']=='9.0_Web_Corpus_Freq')]
#sort and reindex
df4=df4.sort_values(by =['target','lift'],ascending=False,ignore_index=True )
df4.index=df4.index+1
df4

# %%
df_web4

# %%
df_web5

# %%
df_web6=df_web6.loc[df_web6['lift']>1.3]
df6=df_web6.loc[74]
df6

# %%
print(df6.to_latex())

# %%
df_web7

# %%
df_web8

# %%
df_web9

# %%
#store rules in a dictionary
ant_tup=[]
web_tup=[]

for i in range(len(rules)):
    if (rules[i][0]=='4.0_Web_Corpus_Freq' or 
        rules[i][0]=='5.0_Web_Corpus_Freq' or 
        rules[i][0]=='6.0_Web_Corpus_Freq' or 
        rules[i][0]=='7.0_Web_Corpus_Freq' or
        rules[i][0]=='8.0_Web_Corpus_Freq' or
        rules[i][0]=='9.0_Web_Corpus_Freq'):
      if len(rules[i][1])>1: #this ones are cuts at min thresholds (apriori dont work well)
        if rules[i][5]>1.3:
          ant_tup.append(rules[i][1])
          web_tup.append(rules[i][0])

ant_list = [list(ele) for ele in ant_tup]
web_list = [list(ele) for ele in web_tup]

print(ant_list)

#create dictionary between antecedents and Web Corpus Value that they imply
zip_iterator = zip(ant_tup, web_tup)
a_dictionary = dict(zip_iterator)

print(a_dictionary)

# %%
from collections import Counter


list_of_tuples= []
#per ogni regola trovata con questi tagli
for i in range(len(ant_list)):
  ru=ant_list[i] #prendo in considerazione gli antecedenti della regola i
  for j in range(len(X_miss)):
    mi=X_miss[j] #e i valori delle variabili del missing value j
    confront=[k for k in mi if k in ru] #interesezione fra mi e ru
    #sorting
    confront.sort()
    ru.sort()

    #se l'intersezione fra mi e ru corrisponde con ru 
    #allora quella regola riguarda quel missing value 
    if confront==ru:
      confront=tuple(confront)
      #trovami il valore di Web Corpus che implicava quella regola
      value=a_dictionary.get(confront)
      #se sta nel dizionario
      if value!=None:
        #dimmi che parola è
        word=mi[-1]
        #creo tupla con parola di riferimento e valore di Web Corpus
        new_tuple=(word,value)
        #fammi una lista con parola e regola
        list_of_tuples.append(new_tuple)
        #stampami anche gli antecedenti
        print(confront)
        #contami quante sono le regola trovate che riguardano i miei missing values
Counter(list_of_tuples)

        #print("\n word:",mi[-1],value,"\n \n rule:",confront)

# %%
#puoi fare la stessa cosa di sopra col dataframe, ma è più tricky e c'è qualche bug
te_ary_rules=te.fit(ant_list).transform(ant_list)

df_rules_encoded=pd.DataFrame(te_ary_rules,columns=te.columns_)

df_rules_missing=pd.DataFrame()
column_names_miss=list(df_miss_encoded.columns.values)


#col_names=[list(ele) for ele in row (df == 'True').idxmax(axis=1)[row])]
for row in range(len(df_rules_encoded)):
  col_names=df_rules_encoded.columns[(df_rules_encoded == True).iloc[row]].values.tolist()
  column_names=list(set(column_names_miss).intersection(col_names))
  #col_names=(df == 'True').idxmax(axis=1)[row]
  #col_names=df_rules_encoded.apply(lambda row: row[row == 'True'].index, axis=1)
  #col_name=get_col_name(row)
  for row1 in range(len(df_miss_encoded)):
    temp=df_miss_encoded.columns[(df_miss_encoded == True).iloc[row1]].values.tolist()
    confront=list(set(temp).intersection(column_names))
    confront.sort()
    column_names.sort()

    if confront == column_names:
      confront=tuple(confront)
      #print(list(map(a_dictionary.get, confront)), temp[-1])
      print("\n word:",temp[-1],a_dictionary.get(confront),"\n \n rule:",confront)
    #df_miss_encoded[df_miss_encoded.loc[row1,column_names]


#df_rules_missing=pd.merge(df_miss_encoded, df_rules_encoded, on = column_names, how='inner')
#print(df_rules_missing.columns[(df_rules_missing == True).iloc[row]].values.tolist())
#df_rules_missing

# %% [markdown]
# 


