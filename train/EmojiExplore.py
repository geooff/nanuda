#!/usr/bin/env python
# coding: utf-8

# In[26]:


from fastai.text.all import *
import pandas as pd

df = pd.read_parquet("storage/processed-all-emoji-10000-25000.parquet")


# In[29]:


df = df.sample(frac=0.2)


# In[30]:


df.shape


# In[31]:


df.label.str.split(",").explode().value_counts()


# In[32]:


# Language model data
dls_lm = TextDataLoaders.from_df(df, is_lm=True, seq_len=84)
dls_lm.show_batch(max_n=2)


# In[ ]:


# Create our language model
learn = language_model_learner(dls_lm, AWD_LSTM, drop_mult=0.3, metrics=[accuracy, Perplexity()],).to_fp16()
# learn.lr_find()
learn.fit_one_cycle(3, 3e-2)
learn.save_encoder('lm-all-emoji-0.2')


# In[16]:


TEXT = "I am sick of"
N_WORDS = 40
N_SENTENCES = 2
preds = [learn.predict(TEXT, N_WORDS, temperature=0.75) for _ in range(N_SENTENCES)]
print("\n".join(preds))


# In[25]:


# Classifier model data
emoji_clas = DataBlock(
    blocks=(TextBlock.from_df('text', vocab=dls_lm.vocab,), MultiCategoryBlock),
    get_x=ColReader('text'), get_y=ColReader('label', label_delim=','), splitter=ColSplitter())

emoji_clas = emoji_clas.dataloaders(df, seq_len=84)
emoji_clas.show_batch(max_n=2)


# In[32]:


from fastai.losses import *

thresh = 0.0015
multi = partial(accuracy_multi, thresh=thresh)
learn = text_classifier_learner(emoji_clas, 
                                AWD_LSTM,
                                metrics=[FBetaMulti(beta=1.5, thresh=thresh),
                                         HammingLossMulti(thresh=thresh),
                                        multi]).to_fp16()

learn = learn.load_encoder('lm-all-emoji-sample')
learn.lr_find()


# In[ ]:


learn.freeze()
learn.fit_one_cycle(1, 5e-2)

learn.freeze_to(-2)
learn.fit_one_cycle(1, slice(1e-2/(2.6**4),2e-2))

learn.freeze_to(-3)
learn.fit_one_cycle(1, slice(5e-3/(2.6**4),5e-3))

learn.unfreeze()
learn.fit_one_cycle(1, slice(1e-3/(2.6**4),5e-3))

# learn.fine_tune(3, freeze_epochs=4)

# w/ 5% of DS
# LM: 3
# 6, 1, 1, 1
# 2.5% T @ beta=1.5
# Fbeta: 0.197047, Hamming: 0.112834

# 1.0% T @ beta=1.5
# Fbeta: 0.115543, Hamming: 0.308737

# w/ Sample 33%, 2.5% T, beta=1.5
# LM: 3
# Cla: 2, 2, 2, 2
# Fbeta: 0.244360, Hamming: 0.588927

# w/ Sample 33%, 2.5% T, beta=1.5
# LM: 4
# Cla: 2, 2, 2, 2
# Fbeta: 0.243481, Hamming: 0.590672

# w/ Sample 40%, 2.5% T, beta=1.5
# LM: 3
# Cla: 2, 2, 2, 2
# Fbeta: 0.246104, Hamming:0.592116

# w/ Sample 40%, 15% T, beta=1.5
# LM: 3
# Cla: 2, 2, 2, 2
# Fbeta: 0.342252, Hamming: 0.083045


# In[7]:


# learn.export("all-emoji-sample-40")
learn = load_learner("all-emoji-sample-40")


# In[8]:


labels = learn.dls.vocab[1]

def return_label(row):
    result = []
    for idx, val in enumerate(row):
        if val > thresh:
            result.append(labels[idx])
    
    return "".join(result)
    
    
preds, targs = learn.get_preds()
df_preds = pd.DataFrame(preds)
df_preds["pred"] = df_preds.apply(return_label, axis=1)
print("Of "+str(df_preds.shape[0])+" values predicted "+str(df_preds[df_preds["pred"] != ""].shape[0])+" Non-Null results")


# In[9]:


df[df.is_valid == False].sample(5).head()


# In[30]:


preds, targs = learn.get_preds()
xs = torch.linspace(0.01,0.25,290)
accs = [accuracy_multi(preds, targs, thresh=i, sigmoid=False) for i in xs]
plt.plot(xs,accs);


# In[10]:





# In[24]:


labels = learn.dls.vocab[1]

def serve(predicte):
    confidences = learn.predict(predicte)[2].tolist()
    results = {l: c for l, c in zip(labels, confidences)}
    results = sorted(results.items(), key=lambda x: x[1], reverse=True)    
    return results

serve("RIP lil peep")


# In[ ]:




