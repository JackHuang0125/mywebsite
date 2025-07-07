+++
title = "RandomForest Learning"
date = 2025-03-05T11:30:00+08:00
draft =  false
tags = ["Learninig Record", "Ensemble"]
categories = ["Learning"]

[cover]
    image =  "RF.png"
    alt = '20250305'
    caption = 'RF.png by ChatGpt 4o'
+++

#### 這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD

### 🌳 隨機森林基本概要  
由多棵決策樹聚集而成的森林  
方法:  
從原始資料中以取後放回的方式抽取資料，建立每棵決策樹的訓練資料(training datasets)  
因此有些樣本會被重複選中，這樣的抽樣法又稱為Boostraping(拔靴法)  
但是當原始資料的數據龐大時，會發現在抽樣完畢後，有些樣本並沒有被抽取到  
而這些樣本就被稱為Out of Bag(OOB)資料(袋外)  
除了上述訓練資料是被重複抽取之外，特徵也是如此  
隨機森林並不會將所有特徵一起考慮，而是會隨機抽取特徵(可設定參數max_features)  
進行每棵樹的訓練，以上述兩種方式來達到每棵樹近乎獨立的情況，目的是降低每棵樹之間的高度相關性，  
優點是提高模型的泛化能力，防止過擬合(Overfitting)的情況發生、增進預測穩定性與準確度  
演算法:
隨機森林的演算法與決策樹的演算法的核心概念是一樣的，差別只是在建立樹的方法不同而已(如上述)  
意即當應用在分類問題時，則採用吉尼不純度(Gini Impurity)或是鏑(Entropy)演算法作為分類依據  
當應用在迴歸問題時，通常採用最小平方誤差(MSE)(其他還有卜氏Possion)
