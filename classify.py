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
path = os.path.dirname(os.getcwd())
print(path)
sampling_rate = 4000

#############################################################
#load feature vectors
def train(snoring_path, no_snoring_path):
    i = 0
    s1 = s2 = 0
    iters = 20
    settings = "new-new-1"
    while(i < iters):
        print(i)
        snoring_fea_vecs = np.load(path + snoring_path)
        n1 = snoring_fea_vecs.shape[0]
        no_snoring_fea_vecs = np.load(path + no_snoring_path)
        n2 = no_snoring_fea_vecs.shape[0]
        random.shuffle(snoring_fea_vecs)
        random.shuffle(no_snoring_fea_vecs)
        n = 100000
        X = np.concatenate((snoring_fea_vecs[:n], no_snoring_fea_vecs[:n]), axis=0)
        Y = [0]*n + [1]*n

        t1 = time.time()
        #SVM linear
        # clf = svm.SVC(C = 100, kernel='linear', gamma='scale')
        # clf.fit(X,Y)
        # pickle.dump(clf, open(path + "/model/" + settings + "/model_SVM_linear.w",'wb')) 

        #SVM rbf
        clf = svm.SVC(C=100, kernel='rbf', gamma='scale')
        clf.fit(X,Y)
        pickle.dump(clf, open(path + "/model/" + settings + "/model_SVM_rbf.w",'wb'))

        
        #SVM poly
        # clf = svm.SVC(kernel='poly', gamma='scale')
        # clf.fit(X,Y)
        # pickle.dump(clf, open(path + "/model/" + settings + "/model_SVM_poly.w",'wb'))

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
        m = 13000
        r1 = np.sum(1-clf.predict(snoring_fea_vecs[n:n+m]))/(m)
        if(r1 < 0.5):
            r1 = 1 - r1
        s1 = s1 + r1
        r2 = np.sum(clf.predict(no_snoring_fea_vecs[n:n+m]))/(m)
        if(r2 < 0.5):
            r2 = 1 - r2
        s2 = s2 + r2
        t2 = time.time()
        print("testing time:", (t2-t1)/m)
        i = i + 1

    print(s1/iters, s2/iters)

def cross_test(model_name, snoring_path, no_snoring_path):
    #load model
    model = pickle.load(open(path + model_name, 'rb'))
    snoring_fea_vecs = np.load(path + snoring_path)
    n1 = snoring_fea_vecs.shape[0]
    no_snoring_fea_vecs = np.load(path + no_snoring_path)
    n2 = no_snoring_fea_vecs.shape[0]

    r1 = np.sum(1 - model.predict(snoring_fea_vecs))/n1
    r2 = np.sum(model.predict(no_snoring_fea_vecs))/n2
    # print(snoring_fea_vecs[:50])
    # print(no_snoring_fea_vecs[:50])
    print(r1, r2)

train('/feature/snoring_new_6mean_n.npy', '/feature/none_snoring_new_6mean_n.npy')
# cross_test("/model/old-old-1/model_DT.w" ,'/feature/snoring_100_6mean_n.npy', '/feature/none_snoring_100_6mean_n.npy')
# cross_test("/model/old-old-1/model_SVM_rbf.w" ,'/feature/snoring_100_6mean_n.npy', '/feature/none_snoring_100_6mean_n.npy')
# cross_test("/model/old-old-1/model_NB.w" ,'/feature/snoring_100_6mean_n.npy', '/feature/none_snoring_100_6mean_n.npy')
# cross_test("/model/old-old-1/model_LR.w" ,'/feature/snoring_100_6mean_n.npy', '/feature/none_snoring_100_6mean_n.npy')
# cross_test("/model/old-old-1/model_LDA.w" ,'/feature/snoring_100_6mean_n.npy', '/feature/none_snoring_100_6mean_n.npy')
# cross_test("/model/old-old-1/model_GMM.w" ,'/feature/snoring_100_6mean_n.npy', '/feature/none_snoring_100_6mean_n.npy')

