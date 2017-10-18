import read_pose_json as tools
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.externals import joblib
import itertools
import matplotlib
import matplotlib.pyplot as plt
import os


def plot_predictions(strokes_percentage):

    x = [0,1,2,3,4,5]
    strokes_xticks = ['Smash','Lift', 'Net', 'Drive', 'Serve']

    figure, ax = plt.subplots()

    bar_width = 0.50
    bar0 = plt.bar(0, strokes_percentage[0], bar_width, align='center')
    bar1 = plt.bar(1, strokes_percentage[1], bar_width, align='center')
    bar2 = plt.bar(2, strokes_percentage[2], bar_width, align='center')
    bar3 = plt.bar(3, strokes_percentage[3], bar_width, align='center')
    bar4 = plt.bar(4, strokes_percentage[4], bar_width, align='center')

    plt.xlabel('Badminton Strokes')
    plt.ylabel('Percentage of strokes')
    plt.xticks(x,strokes_xticks)
    plt.title('Frequency of badminton strokes')
    #plt.savefig('output/fig.png')

    return figure, ax

"""
Function : predict_badminton_strokes
Input : Takes in the directory of the csv for the athlete poses
Output : Predicts the different strokes in the pose and returns the prediction only


"""

def predict_badminton_strokes(csv_dir):
    X = []

    athlete_data = tools.read_from_csv(csv_dir)
    for athlete in athlete_data:
        X.append(map(float, athlete[0:28])) #Truncate features for X for prediction - eyes and ears are removed

    #Load trained model
    neural_model_dir = os.pardir + '/FYP_MLP.pkl'
    mlp = joblib.load(neural_model_dir)
    predictions = mlp.predict(X)

    return predictions

def predict_badminton_strokes_list(list_person):
    X = []

    X.append(list(itertools.chain.from_iterable(list_person))) #Convert into a flat list
    X[0] = X[0][0:28]
    neural_model_dir = os.pardir + '/FYP_MLP.pkl'
    mlp = joblib.load(neural_model_dir)
    predictions = mlp.predict(X)

    return predictions

def calc_percentage_strokes(predictions):
    # Smash, lift, net, drive, serve
    strokes = [0, 0, 0, 0, 0]
    strokes_percentage = [0.0, 0.0, 0.0, 0.0, 0.0]

    for index, value in enumerate(predictions):
        strokes[value] += 1

    total_prediction = sum(strokes)
    for j in range(5):
        strokes_percentage[j] = (float(strokes[j]) / total_prediction) * 100

    return strokes_percentage


def calc_playstyle(strokes_percentage):

    lowest_index = strokes_percentage.index(min(strokes_percentage))
    highest_index = strokes_percentage.index(max(strokes_percentage))

    #Should improve the if elif to be more accurate

    if highest_index is 0 or highest_index is 2:
        playstyle = "Offensive"
    elif highest_index is 1 or highest_index is 4:
        playstyle = "Defensive"
    else:
        playstyle = "Neutral"

    return playstyle

"""


csv_dir = '/home/tmk/Downloads/athlete_data.csv'
athlete_data = tools.read_from_csv(csv_dir)

#Set up data for training
# X is features while Y is target label
X = []
Y = []
for athlete in athlete_data:
    #Truncate to only 28 features for X, remaining features not required - eye and ear are removed
    X.append(map(float,athlete[0:28]))
    Y.append(map(int,athlete[36]))


#Split data into training and testing
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, train_size = 0.80)

#Convert list of lists --> list
Y_train = list(itertools.chain(*Y_train))
Y_test = list(itertools.chain(*Y_test))

#Create the multi layer perceptron
#Parameter details : http://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html

mlp = MLPClassifier(hidden_layer_sizes=(28,28), activation='relu', max_iter=1000, verbose=True)
mlp.fit(X_train,Y_train)
predictions = mlp.predict(X_test)

joblib.dump(mlp,'FYP_MLP.pkl')

print(classification_report(Y_test,predictions))
plot_predictions(predictions)

"""