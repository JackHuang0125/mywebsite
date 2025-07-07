+++
title = "Text Mining with R: Chapter3"
date = 2025-01-24T15:02:00+08:00
draft =  false
tags = ["Learninig Record", "Text mining"]
categories = ["Learning"]

[cover]
    image =  "wordcloud.png"
    alt = '20250124'
    caption = 'wordcloud.png by JackHuang'
+++

**這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD**  

### Analyzing word and document frequency: tf-idf  
1. Term Frequency(tf): How frequently a word occurs in a document  
詞頻: 單詞出現在文檔的頻率
2. Inverse Document Frequency(idf): use to decrease the weight for commonly used words and increase the weight for words that are not used very much in a collection of documents  
逆文檔頻率: 文檔中出現愈多次的單詞，其權重愈低；反之則愈低。即衡量某詞在所有文檔中分佈的稀疏程度，是一種懲罰項 。 
並定義為：
$$idf(term) = ln\left(\frac{n_{documents}}{n_{documents containing term}}\right)$$
其中分子$n_{documents}$是文檔總數，分母$n_{documents containing term}$是包含該詞的文檔總數，
若某單詞出現在文檔的次數少，表示分母小，其 IDF 大，重要性高，權重高；反之出現的次數多，表示分母大，其 IDF 小，重要性低，權重低。
取對數則是為了減少極端數值，使 IDF 分佈更加平滑。  

**tf-idf的目標是用於識別在單一文檔中有價值、但不常見的單詞（詞彙）**  

### Zipf's law ( 齊夫定律)
1. 一種描述自然語言中單詞使用頻率分佈的統計規律，其宣稱單詞的頻率與其在文檔裡的頻率排名成反比，即：$$frequency \propto \frac{1}{rank} $$
2. 出現頻率第一名的單詞的次數會是出現頻率第二名的單詞的次數的兩倍，會是出現頻率第三名的單詞的次數的三倍...依此類推，會是出現頻率第 N 名的單詞的次數的 N 倍
3. 若將排名 x 與出現頻率 y 取對數，即 logx 、 logy ，若整個文檔的坐標點標出來接近一直線，則該文檔符合 Zipf's law  

