---
title: Pop Quiz - Algorithms
date: 2017-11-25T07:49:37+00:00
author: Taylor Murphy
layout: post
permalink: /algorithms/
---
I was recently quizzed over the phone about my algorithmic knowledge. I’m, evidently, not the best at defining terms or concepts on the spot, and my answers certainly reflected that. I’ve always struggled with pure memorization of facts, and the pressure of accurately defining them on the spot makes it even worse. But, with that said, these are things I should know, so it’s worth it to take the time to explain and define them in a way that hopefully sticks in my brain better.



**Linear vs Logistic Regression**

There’s something about algorithms and math and the people who name things that makes them want to obfuscate what’s really going on. These should really just be called Continuous Regression and Binary Regression (or Categorical Regression).

In Linear (Continuous) Regression, the outcome (i.e. your dependent variable - dependent meaning its value depends on the other variable) can have any value. An example of this is the work I did in grad school: we’d adjust the concentration of analyte (say, glucose) in our culture medium (the analyte being the independent variable) and see what effect it had on the reaction rates, or fluxes (this was the dependent variable). You would then use linear regression to figure out how glucose predicts the flux.

In Logistic (Binary/Categorical) Regression, you’re trying to predict a discrete number of events. Using cell growth as an example, a good use for Logistic Regression would be to predict whether the cells grow above or below a certain viability threshold given the glucose concentration in the medium. 



**Random Forests**

I’ve never actually used random forests for my professional work, but they aren’t that bad to grok once you get the hang of it. And they’re actually named fairly well. 

At a high level, random forests are essentially a bunch of decision trees that enable you to predict specific categories (classification) for your data. You take a bunch of these trees (randomly generated), train them on your data, and a lot of them will perform poorly. But enough of them won’t! The predictions of all the models are then combined to give a pretty good prediction model (this is called ensemble learning). The idea being that the bad models will cancel each other out and the good models will win.

I need to spend more time with it, but it seems like it works pretty well for many use cases.



**Regularization**

I’m not a fan of how this is named because it doesn’t bring to mind what it’s actually doing. I’ve been using regularization regularly (yuk yuk yuk) in the Fast.ai course I’m working my way through, but I didn’t have a strong definition of it in my head. Regularization is essential a tool for reducing overfitting (overfitting being the inability of a model to generalize its predictions well).

For neural networks, we’ve been using random dropout (literally setting random weights to zero) on the network for regularization. The regularization that most people talk about is L1 vs L2. Simply put, these regularization techniques add to the objective function of the model (probably sum of squared errors) via either the sum of absolute value of the weights or the sum of squares of the weights, respectively. It’s trying to control the model complexity by adding a penalty to it for when overfitting happens. Maybe a better name for it is penalization?

Regularization is actually one of 5 recommended techniques for reducing overfitting. The recommendation comes from the fast.ai course:

1. Add more data
1. Data Augmentation - (for images this would be shifting, rotating, and skewing the images)
1. Using generalizable architectures - meaning batch normalization in the scope of this course
1. Regularization
1. Reduce architecture complexity

So, you can see that it’s actually lower on the list of things you can do to reduce overfitting. All of the other methods could be their own post / explanation (except, I guess, adding more data…).

Well, there you have it. Things I should know and could reasonably explain given time, but the spur of the moment questions just aren’t my bag. Hopefully, this is helpful to people in the future that need a more human-understandable definition.
