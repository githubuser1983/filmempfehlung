#!/usr/bin/python

# found at:
# http://fa.bianp.net/blog/2012/learning-to-rank-with-scikit-learn-the-pairwise-transform/

import itertools
import numpy as np
from scipy import stats
import pylab as pl
from sklearn import svm, linear_model, cross_validation

np.random.seed(0)
theta = np.deg2rad(60)
w = np.array([np.sin(theta), np.cos(theta)])
K = 20
X = np.random.randn(K, 2)
y = [0] * K
for i in range(1, 3):
    X = np.concatenate((X, np.random.randn(K, 2) + i * 4 * w))
    y = np.concatenate((y, [i] * K))

# slightly displace data corresponding to our second partition
X[::2] -= np.array([3, 7]) 
blocks = np.array([0, 1] * (X.shape[0] / 2))

# split into train and test set
cv = cross_validation.StratifiedShuffleSplit(y, test_size=.5)
train, test = iter(cv).next()
X_train, y_train, b_train = X[train], y[train], blocks[train]
X_test, y_test, b_test = X[test], y[test], blocks[test]

# plot the result
idx = (b_train == 0)
pl.scatter(X_train[idx, 0], X_train[idx, 1], c=y_train[idx], 
    marker='^', cmap=pl.cm.Blues, s=100)
pl.scatter(X_train[~idx, 0], X_train[~idx, 1], c=y_train[~idx],
    marker='o', cmap=pl.cm.Blues, s=100)
pl.arrow(0, 0, 8 * w[0], 8 * w[1], fc='gray', ec='gray', 
    head_width=0.5, head_length=0.5)
pl.text(0, 1, '$w$', fontsize=20)
pl.arrow(-3, -8, 8 * w[0], 8 * w[1], fc='gray', ec='gray', 
    head_width=0.5, head_length=0.5)
pl.text(-2.6, -7, '$w$', fontsize=20)
pl.axis('equal')
pl.show()

print "eingabetaste weiter..."
raw_input()

ridge = linear_model.Ridge(1.)
ridge.fit(X_train, y_train)
coef = ridge.coef_ / np.linalg.norm(ridge.coef_)
pl.scatter(X_train[idx, 0], X_train[idx, 1], c=y_train[idx], 
    marker='^', cmap=pl.cm.Blues, s=100)
pl.scatter(X_train[~idx, 0], X_train[~idx, 1], c=y_train[~idx],
    marker='o', cmap=pl.cm.Blues, s=100)
pl.arrow(0, 0, 7 * coef[0], 7 * coef[1], fc='gray', ec='gray', 
    head_width=0.5, head_length=0.5)
pl.text(2, 0, '$\hat{w}$', fontsize=20)
pl.axis('equal')
pl.title('Estimation by Ridge regression')
pl.show()


print "eingabetaste weiter..."
raw_input()   

for i in range(2):
    tau, _ = stats.kendalltau(
        ridge.predict(X_test[b_test == i]), y_test[b_test == i])
    print('Kendall correlation coefficient for block %s: %.5f' % (i, tau))

print "eingabetaste weiter..."
raw_input()   

# form all pairwise combinations
comb = itertools.combinations(range(X_train.shape[0]), 2)
k = 0
Xp, yp, diff = [], [], []
for (i, j) in comb:
    if y_train[i] == y_train[j] \
        or blocks[train][i] != blocks[train][j]:
        # skip if same target or different group
        continue
    Xp.append(X_train[i] - X_train[j])
    diff.append(y_train[i] - y_train[j])
    yp.append(np.sign(diff[-1]))
    # output balanced classes
    if yp[-1] != (-1) ** k:
        yp[-1] *= -1
        Xp[-1] *= -1
        diff[-1] *= -1
    k += 1
Xp, yp, diff = map(np.asanyarray, (Xp, yp, diff))
pl.scatter(Xp[:, 0], Xp[:, 1], c=diff, s=60, marker='o', cmap=pl.cm.Blues)
x_space = np.linspace(-10, 10)
pl.plot(x_space * w[1], - x_space * w[0], color='gray')
pl.text(3, -4, '$\{x^T w = 0\}$', fontsize=17)
pl.axis('equal')
pl.show()


print "eingabetaste weiter..."
raw_input()

clf = svm.SVC(kernel='linear', C=.1)
clf.fit(Xp, yp)
coef = clf.coef_.ravel() / np.linalg.norm(clf.coef_)
pl.scatter(X_train[idx, 0], X_train[idx, 1], c=y_train[idx],
    marker='^', cmap=pl.cm.Blues, s=100)
pl.scatter(X_train[~idx, 0], X_train[~idx, 1], c=y_train[~idx],
    marker='o', cmap=pl.cm.Blues, s=100)
pl.arrow(0, 0, 7 * coef[0], 7 * coef[1], fc='gray', ec='gray',
    head_width=0.5, head_length=0.5)
pl.arrow(-3, -8, 7 * coef[0], 7 * coef[1], fc='gray', ec='gray',
    head_width=0.5, head_length=0.5)
pl.text(1, .7, '$\hat{w}$', fontsize=20)
pl.text(-2.6, -7, '$\hat{w}$', fontsize=20)
pl.axis('equal')
pl.show()


print "eingabetaste weiter..."
raw_input()

for i in range(2):
    tau, _ = stats.kendalltau(
        np.dot(X_test[b_test == i], coef), y_test[b_test == i])
    print('Kendall correlation coefficient for block %s: %.5f' % (i, tau))
