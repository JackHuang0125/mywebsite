+++
title = "Naive & Gaussian Bayes Learning"
date = 2025-03-21T16:40:00+08:00
draft =  false
tags = ["Learninig Record", "Bayes", "Gaussian"]
categories = ["Learning"]

[cover]
    image =  "Bayes.webp"
    alt = '20250322'
    caption = 'Bayes.webp by ChatGpt 4o'
+++

#### 這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD

### 👶 Naive Bayes
By definition of Bayes' theorem
$$
P(y \mid x_1, x_2, ..., x_n) = \frac{P(y)P(x_1, x_2, ..., x_n \mid y)}{P(x_1, x_2, ..., x_n)}
$$

where   
- $P(y)$ represents the prior probability of class $y$
- $P(x_1, x_2, ..., x_n \mid y)$ represents the likelihood, i.e., the probability of observing features $x_1, x_2, ..., x_n$ given class $y$
- $P(x_1, x_2, ..., x_n)$ represents the marginal probability of the feature set $x_1, x_2, ..., x_n$

With the assumption of Naive Bayes - **Conditional Independence**  
$$
P(x_i \mid y, x_1, ..., x_{i-1}, x_{i+1}, ..., x_n) = P(x_i \mid y)
$$

This means that the probability of feature $x_i$ is no longer influenced by other features $x_j$ for $j \not= x $ given the class y is known

Therefore, we have
$$
\begin{aligned}
P(x_1, x_2, ..., x_n \mid y) 
&= P(x_1 \mid y)P(x_2 \mid y)...P(x_n \mid y) \\\\
&= \prod_{i=1}^nP(x_i \mid y)
\end{aligned}
$$

This relationship implies that
$$
P(y \mid x_1, x_2, ..., x_n) = \frac{P(y)\prod_{i=1}^nP(x_i \mid y)}{P(x_1, x_2, ..., x_n)}
$$

Since $P(x_1, x_2, ..., x_n)$ is constant given the input, we can use the following classification rule
$$
P(y \mid x_1, x_2, ..., x_n) \propto P(y)\prod_{i=1}^nP(x_i \mid y)
$$

### 👉 Finally, we have
$$
\hat{y} = \arg \max_y P(y)\prod_{i=1}^nP(x_i \mid y)
$$

And we can use Maximum A Posteriori (MAP) estimation to estimate $P(y)$ and $P(x_i \mid y)$, and the former is then the relative frequency of class in the training set.

---
### In the other hand, 
in **likelihood ratio form**, we suppose that
$$
P(C=+\mid X) = \frac{P(C=+)P(X \mid C=+)}{P(X)}
$$

$$
P(C=-\mid X) = \frac{P(C=-)P(X \mid C=-)}{P(X)}
$$

for two classes, $C=+$ and $C=-$

And $X$ is classifed as the class $C=+$ if and only if 
$$
f_b(X) = \frac{P(C=+\mid X)}{P(C=-\mid X)} \ge 1
$$

Moreover, 
$$
f_b(X) = \frac{P(C=+\mid X)}{P(C=-\mid X)} = \frac{P(C=+)P(X\mid C=+)}{P(C=-)P(X\mid C=-)}
$$

where $f_b(X)$ is called a **Bayesian classifier**.

As we know that 
$$
P(X \mid y) = \prod_{i=1}^nP(x_i \mid y)
$$

Finally, we have
$$
\begin{aligned}
f_{nb}(X)
&=  \frac{P(C=+)P(X\mid C=+)}{P(C=-)P(X\mid C=-)} \\\\
&= \frac{P(C=+)\prod_{i=1}^nP(x_i \mid C=+)}{P(C=-)\prod_{i=1}^nP(x_i \mid C=-)}
\end{aligned}
$$

if
$$
f_{nb}(X) \ge1 \Rightarrow predict\ as\ class +1
$$

$$
f_{nb}(X) <1 \Rightarrow predict\ as\ class -1
$$

where $f_{nb}(X)$ is called a **naive Bayesian classifier**,
or simply naive Bayes (NB).

>
Figure 1 shows an example of
naive Bayes. In naive Bayes, each attribute node has no parent except the class node.[1]
![targets](/images/bayes.png)

---
### 🤴 Gaussian Naive Bayes
> When dealing with continuous data, a typical supposition is that the continuous values correlating with every class are distributed acceding to Gaussian distribution. The training data are splitted by class and the mean and stander deviation of every class is calculated. Therefore for estimating the probabilities of continuous data set the following equation can be [2]

$$
P(x_i \mid y) = \frac{1}{\sqrt{2\pi\sigma^2_y}}exp(-\frac{(x_i-\mu_y)^2}{2\sigma^2_y})
$$

where
- $\mu_y$: the mean of the $i$-th feature under class $y$
- $\sigma_y$: the variance of the $i$-th feature under class $y$

For the new data set $X'_j$, we use this equation to calculate
$$
P(y \mid X'_j) \propto P(y)\prod_{j=1}^nP(x_j \mid y)
$$

---

### 🔧 Modeling with Gaussian Naive Bayes
```python
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix
data = load_iris()
X = data.data
y = data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
gnb = GaussianNB()
model = gnb.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
-----------------------------------------
0.9777777777777777
[[19  0  0]
 [ 0 12  1]
 [ 0  0 13]]
```

---
### 📖 Reference
[1] [Zhang, H. (2004). The optimality of naive Bayes. Aa, 1(2), 3.](https://www.cs.unb.ca/~hzhang/publications/FLAIRS04ZhangH.pdf)  
[2] [Kamel, H., Abdulah, D., & Al-Tuwaijari, J. M. (2019, June). Cancer classification using gaussian naive bayes algorithm. In 2019 international engineering conference (IEC) (pp. 165-170). IEEE.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8950650)  
[3] [Scikit-learn](https://scikit-learn.org/stable/modules/naive_bayes.html)  
[4] [貝氏分類器(Naive Bayes Classifier)(含python實作), Roger Yong, 2021](https://roger010620.medium.com/%E8%B2%9D%E6%B0%8F%E5%88%86%E9%A1%9E%E5%99%A8-naive-bayes-classifier-%E5%90%ABpython%E5%AF%A6%E4%BD%9C-66701688db02)