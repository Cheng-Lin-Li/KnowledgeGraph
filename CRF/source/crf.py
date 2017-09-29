'''
Conditional Random Field (CRF) for Information Extraction
This tasks will leverage CRF to perform information extraction from un-structure texts.
The target un-structure texts come from syllabus of Harvard extension school. 
The authors and publish year of textbooks would be extracted by the trained CRF model.

Created on Sep 23, 2017

@author: Cheng-Lin Li
@reference: https://github.com/scrapinghub/python-crfsuite/blob/master/examples/CoNLL%202002.ipynb
@reference: https://python-crfsuite.readthedocs.io/en/latest/
'''
import sys, time, string
from itertools import chain
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
import pycrfsuite


def get_input (input_file):
    '''
    get input file by utf8 encoding. Read the file content then return it.
    '''
    sentence = []
    result_list = []

    with open(input_file, 'r', encoding='utf8') as f:
        for i in f.readlines():
            data = tuple(i.replace('\n', '').replace('\ufeff', '').split('|')) # Remove BOM
            if data == ('',): # end of sentence
                result_list.append(sentence)
                sentence = []
            else:
                sentence.append(data)
        f.close()    
    return result_list

def set_features(sentence, i):
    '''
    Set features for each word in a sentence.
    '''
    word = sentence[i][0]
    
    # Set the features of the word
    features = [
        'word.lower=' + word.lower(),
        'word.length=' + str(len(word)),
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'word.isdot=%s' % isdot(word),    
        'word.isdash=%s' % isdash(word),          
        'word.iscomma=%s' % iscomma(word),
    ]
    if i > 0:
        # Set the features of relationship with previous word.
        word1 = sentence[i-1][0]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.length=' + str(len(word1)),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isdigit=%s' % word1.isdigit(), 
            '-1:word.isdot=%s' % isdot(word1),    
            '-1:word.isdash=%s' % isdash(word1),  
            '-1:word.iscomma=%s' % iscomma(word1),         
        ])
    else:
        features.append('Begin_Of_Sentence')
        
    if i < len(sentence)-1:
        # Set the features of relationship with next word.
        word1 = sentence[i+1][0]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.length=' + str(len(word1)),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:word.isdot=%s' % isdot(word1),    
            '+1:word.isdash=%s' % isdash(word1),  
            '+1:word.iscomma=%s' % iscomma(word1), 
        ])
    else:
        features.append('End_Of_Sentence')
                
    return features

def isdot(word):
    return True if word in '.' else False

def isdash(word):
    return True if word in '-' else False

def iscomma(word):
    return True if word in ',' else False

def ispunchuation(word):
    return True if word in string.punctuation else False

def get_features(sent):
    return [set_features(sent, i) for i in range(len(sent))]

def get_labels(sent):
    return [label for _token, label in sent]

def get_tokens(sent):
    return [token for token, _label in sent]     
    
def bio_classification_report(y_true, y_pred):
    '''
    Classification report for a list of BIO-encoded sequences.
    It computes token-level metrics and discards "N" labels.
    
    Note that it requires scikit-learn 0.15+ (or a version from github master) to calculate averages properly!
    '''
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))
        
    tagset = set(lb.classes_) - {'N'}
    tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}
    
    return classification_report(
        y_true_combined,
        y_pred_combined,
        labels = [class_indices[cls] for cls in tagset],
        target_names = tagset,
    )
    

def main(training_file, testing_file, model_file):
    
    start = time.time()
    
    # Get training and testing set of data
    training_set = get_input(training_file)
    testing_set = get_input(testing_file)
    
    # Get features of each word on training set
    X_train = [get_features(s) for s in training_set]
    y_train = [get_labels(s) for s in training_set]
    
    # Get features of each word on testing set
    X_test = [get_features(s) for s in testing_set]
    y_test = [get_labels(s) for s in testing_set]

    # Create trainer model of CRF
    trainer = pycrfsuite.Trainer(verbose=False)

    for xseq, yseq in zip(X_train, y_train):
        trainer.append(xseq, yseq)

    trainer.set_params({
        'c1': 0.5,   # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 1000,  # stop earlier
    
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })    
    
    # Train the model and save the trained model into model_file
    trainer.train(model_file)
    print ('Log of last iteration=%s'%(trainer.logparser.iterations[-1]))

    # Initial tagger for prediction task
    trained_model = pycrfsuite.Tagger()
    trained_model.open(model_file) # Load the trained model.
        
    # Get prediction tag results from trained model
    y_pred = [trained_model.tag(xseq) for xseq in X_test]
    
    # Print the Precision, Recall, and F-1 score
    print(bio_classification_report(y_test, y_pred))
    
    end = time.time()
    print('CRF model has been generated.')
    print('runtime:', end - start)
    


if __name__ == '__main__':
    
    # Get input and output parameters
    if len(sys.argv) < 4:
        print('Usage: python ' + sys.argv[0] + ' <training data input file> <testing data input file> <model file name>')
        print('       The program requires Python 3.6 to execute.')
        print('       Note that it requires scikit-learn 0.15+ (or a version from github master to calculate averages properly!')
        print('       - training data input file : Tokenized training data input file location.')     
        print('       - testing data input file = Tokenized testing data input file location.')      
        print('       - model file name = Trained CRF model file path and name.')                                          
        exit ()    

    if len(sys.argv) == 4:           
        training_file = sys.argv[1]
        testing_file = sys.argv[2]
        model_file = sys.argv[3]

        main(training_file, testing_file, model_file)
        