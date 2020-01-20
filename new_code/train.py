import numpy as np
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier
import os
import time
import pickle
import random

#############################################################
path = os.getcwd()
print(path)
sampling_rate = 4000

#############################################################
#load feature vectors
def train(file_name):
    
    snoring_fea_vecs = np.load(path + "/feature/snoring_" + file_name + ".npy")
    no_snoring_fea_vecs = np.load(path + "/feature/non_snoring_" + file_name  + ".npy")
    n1 = snoring_fea_vecs.shape[0]
    n2 = no_snoring_fea_vecs.shape[0]
    n2 = int(n1)
    print(n1, n2)

    settings = "model" + file_name

    np.random.shuffle(snoring_fea_vecs)
    np.random.shuffle(no_snoring_fea_vecs)

    X = np.concatenate([snoring_fea_vecs, no_snoring_fea_vecs[:n2]], axis=0)
    Y = [0]*n1 + [1]*n2
    t1 = time.time()
    #SVM linear
    clf = svm.SVC(C = 100, kernel='rbf', gamma='scale')
    clf.fit(X,Y)
    pickle.dump(clf, open(path + "/model/" + settings + "/stats_model_SVM_linear.w",'wb')) 

    #train NB
    # clf = GaussianNB()
    # clf.fit(X, Y)
    # pickle.dump(clf, open(path + "/model/" + settings + "/model_NB.w",'wb'))

    #logistic
    # clf = LogisticRegression(random_state=0, solver='lbfgs')
    # clf.fit(X, Y)
    # pickle.dump(clf, open(path + "/model/" + settings + "/model_LR.w",'wb'))

    #tree
    # clf = DecisionTreeClassifier()
    # clf.fit(X, Y)
    # pickle.dump(clf, open(path + "/model/" + settings + "/model_DT.w",'wb'))

    #LDA
    # clf = LinearDiscriminantAnalysis()
    # clf.fit(X, Y)
    # pickle.dump(clf, open(path + "/model/" + settings + "/model_LDA.w",'wb'))

    #GMM
    # clf = GaussianMixture(n_components=2)
    # clf.fit(X)
    # pickle.dump(clf, open(path + "/model/" + settings + "/model_GMM.w",'wb'))

    t2 = time.time()
    print("training time:", t2-t1)

    t1 = time.time()
    r1 = np.sum(1-clf.predict(snoring_fea_vecs[:n1]))/(n1)
    if(r1 < 0.5):
        r1 = 1 - r1
    print("T", r1)
    n2 = no_snoring_fea_vecs.shape[0]
    r2 = np.sum(clf.predict(no_snoring_fea_vecs[:n2]))/(n2)
    if(r2 < 0.5):
        r2 = 1 - r2
    print("F", r2)
    t2 = time.time()
    print("testing time:", (t2-t1))

for i in [1, 4, 5, 7, 8, 9]:
    train(str(i))

