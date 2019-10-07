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
def train(record):
    snoring_fea_vecs = np.zeros([1, 3])
    no_snoring_fea_vecs = np.zeros([1, 3])
    for i in range(1, 7):
        if(i == record):
            continue
        snoring_fea = np.load(path + "/feature/xsnoring_" + str(i) + ".npy")
        no_snoring_fea = np.load(path + "/feature/xnon_snoring_" + str(i)  + ".npy")
        snoring_fea_vecs = np.concatenate([snoring_fea_vecs, snoring_fea])
        no_snoring_fea_vecs = np.concatenate([no_snoring_fea_vecs, no_snoring_fea])
    no_snoring_fea_vecs = no_snoring_fea_vecs[1:]
    snoring_fea_vecs = snoring_fea_vecs[1:]
    n1 = snoring_fea_vecs.shape[:]
    n2 = no_snoring_fea_vecs.shape[:]
    print(n1, n2)
    iters = 20
    i = 0
    s1 = s2 = 0
    settings = "full"
    log = []
    while(i < iters):
        print(i)
        np.random.shuffle(snoring_fea_vecs)
        np.random.shuffle(no_snoring_fea_vecs)
        
        n1 = 100000
        n2 = 600000
        X = np.concatenate([snoring_fea_vecs[:n1], no_snoring_fea_vecs[:n2]], axis=0)
        Y = [0]*n1 + [1]*n2
        t1 = time.time()
        #SVM linear
        # clf = svm.SVC(C = 100, kernel='linear', gamma='scale')
        # clf.fit(X,Y)
        # pickle.dump(clf, open(path + "/model/" + settings + "/model_SVM_linear.w",'wb')) 

        #train NB
        clf = GaussianNB()
        clf.fit(X, Y)
        pickle.dump(clf, open(path + "/model/" + settings + "/model_NB.w",'wb'))

        #logistic
        # clf = LogisticRegression(random_state=0, solver='lbfgs')
        # clf.fit(X, Y)
        # pickle.dump(clf, open(path + "/model/" + settings + "/model_LR.w",'wb'))

        #tree
        # clf = DecisionTreeClassifier()
        # clf.fit(X, Y)
        # pickle.dump(clf, open(path + "/model/" + settings + "/model_DT.w",'wb'))

        # LDA
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
        m = snoring_fea_vecs.shape[0] - n1
        r1 = np.sum(1-clf.predict(snoring_fea_vecs[n1:]))/(m)
        if(r1 < 0.5):
            r1 = 1 - r1
        s1 = s1 + r1
        print("T", r1)
        
        m = no_snoring_fea_vecs.shape[0] - n2
        r2 = np.sum(clf.predict(no_snoring_fea_vecs[n2:]))/(m)
        if(r2 < 0.5):
            r2 = 1 - r2
        print("F", r2)
        s2 = s2 + r2
        t2 = time.time()
        print("testing time:", (t2-t1))
        i = i + 1
        log.append([r1, r2])
    np.savetxt("log.csv", np.array(log), delimiter=",")
    print(s1/iters, s2/iters)

def cross_test(model_name, snoring_path, no_snoring_path):
    #load model
    model = pickle.load(open(path + model_name, 'rb'))
    snoring_fea_vecs = np.load(path + snoring_path)
    n1 = snoring_fea_vecs.shape[0]
    no_snoring_fea_vecs = np.load(path + no_snoring_path)
    n2 = no_snoring_fea_vecs.shape[0]

    r1 = np.sum(model.predict(snoring_fea_vecs))/n1
    r2 = np.sum(1 - model.predict(no_snoring_fea_vecs))/n2
    print(r1, r2)

train(0)
# cross_test("/model/6/model_GMM.w" ,'/feature/xsnoring_6.npy', '/feature/xnon_snoring_6.npy')

