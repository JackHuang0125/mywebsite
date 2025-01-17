+++
title = "Expectation maximization algorithm"
date = 2025-01-12T11:00:00+08:00
draft =  false
tags = ["Machine Learning", "Learninig Record", "EM"]
categories = ["Learning"]

[cover]
    image =  "EM.jpg"
    alt = '20250112'
    caption = 'EM.jpg by JackHuang'
+++

**這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD**  
1. Expectation-maximization algorithm  
又翻譯為「最大期望值演算法」  
2. 經過兩個步驟交替進行計算：  
第一步是計算期望值（E）：利用對隱藏變量的現有估計值，計算其最大概似估計值  
第二步是最大化（M）：最大化在E步上求得的最大概似值來計算參數的值
M步上找到的參數估計值被用於下一個E步計算中，這個過程不斷交替進行  
**引自維基百科**
```