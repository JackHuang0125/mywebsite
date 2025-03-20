+++
title = "Least square estimator of β in linear regression"
date = 2024-10-04T16:02:00+08:00
draft =  false
tags = ["Linear", 'Regression', 'Estimator']
categories = ["APLM", 'Homework']

[cover]
    image =  "linear.webp"
    alt = '20241004'
    caption = 'linear.webp by GPT 4o'
+++
### Assume
$$ Y_i = \beta_o + \beta_1X_i+\varepsilon_i $$
, for given $n$ observerd data $(x_i, Y_i)$, $\forall i=1～n$


Note that:
$$ Y_i \mid X_i=x_i ~ N(\beta_o+\beta_1X_1, \sigma^2) $$  
$\therefore$
$$ E_{Y \mid X}[Y_i \mid X_i =x_i]=\beta_o+\beta_1X_1$$
In vector notation: 
$$ Y_i = x^T_i\beta + \varepsilon_i $$
where
- $ x_i=(1, X_1, ..., X_n)^T $

And for $ Y = (Y_1, ..., Y_n)^T $, We have: 
$$
Y = X\beta + \varepsilon
$$

where
- $
X =
\begin{bmatrix} 
    1 & X_1 \\\\
    1 & X_2 \\\\ 
    \vdots & \vdots \\\\ 
    1 & X_n
\end{bmatrix}
$

- $ Y = \begin{bmatrix} Y_1 \\\\ Y_2 \\\\ \vdots \\\\ Y_n \end{bmatrix} $,

$
\begin{bmatrix} Y_1 \\\\ Y_2 \\\\ \vdots \\\\ Y_n
\end{bmatrix}= \begin{bmatrix} 1 & X_1 \\\\ 1 & X_2 \\\\ \vdots & \vdots \\\\ 1 & X_n
\end{bmatrix}\begin{bmatrix} \beta_0 \\\\ \beta_1 
\end{bmatrix}+\varepsilon
$

$
Y～N(X\beta, \sigma^2)
$ 
given a joint p.d.f. for $Y$ given $X$ of the form:
$$
f_y(y; \beta, \sigma^2)=
\frac{1}{\sqrt 2\pi\sigma^2}e^{\frac{(y-X\beta)^T(y-X\beta)}{-2\sigma^2}}
$$
consider the maximization for $\beta$ indicates
that:
$$
min \left[(y-X\beta)^T(y-X\beta)\right]
$$
and thus:
$$
\begin{aligned}
    (y - X\beta)^T (y - X\beta) &= (y^T - (X\beta)^T)(y - X\beta) \\\\
    &= (y^T - \beta^T X^T)(y - X\beta) \\\\
    &= y^T y - y^T X\beta - \beta^T X^T y + \beta^T X^T X \beta \\\\
    &= y^T y - 2y^T X\beta + \beta^T X^T X \beta \\\\
    \frac{\partial}{\partial\beta} (y^T y - 2y^T X\beta + \beta^T X^T X \beta)
    &= -2yT^X+2X^TX\beta 
    \overset{\text{Let}}{=}0 \\\\
    X^TX\beta 
    &= y^TX 
\end{aligned}
$$
since $(X^TX)^{-1}$ exists

$\therefore$
$$
\beta = (X^TX)^{-1}X^Ty
$$

### Next time, we will talk about $\beta_0$ and $\beta_1$