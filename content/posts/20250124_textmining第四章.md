+++
title = "Text Mining with R: Chapter4"
date = 2025-01-26T13:45:00+08:00
draft =  false
tags = ["Learninig Record", "Text mining"]
categories = ["Learning"]

[cover]
    image =  "wordcloud.png"
    alt = '20250124'
    caption = 'wordcloud.png by JackHuang'
+++

**這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD**  

### Tokenizing by n-gram (n-gram 分詞)
1. 將文檔的內容依照 n 個單詞作分類，例如：  
[1] "The Bank is a place where you put your money"  
[2] The Bee is an insect that gathers honey"  
我們可以利用函式 tokenize_ngrams() 依照 n = 2 分類為  
[1] "the bank"、"bank is"、"is a"、"a place"、"place where"、"where you"、"you put"、"put your"、"your money"  
[2] "the bee"、"bee is"、"is an"、"an insect"、"insect that"、"that gathers"、"gathers honey"