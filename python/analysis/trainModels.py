from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

def train(X_train_values, y_train_values, X_test_values):
    results = {}
    models = {
        'svr': SVR(kernel='linear', gamma='auto', C=100, epsilon=0.01),
        'kneighbors': KNeighborsRegressor(n_neighbors=10, p=1, weights='distance'),
        'neural_net': MLPRegressor(max_iter=100, activation='tanh', alpha=0.05, hidden_layer_sizes= (50, 100, 50), learning_rate='adaptive', solver='adam'),
        'decision_tree': DecisionTreeRegressor(max_depth=10, max_features=None, min_samples_leaf=1, min_samples_split=10),
        'random_forest': RandomForestRegressor(max_depth= None, max_features= 'sqrt', min_samples_leaf= 1, min_samples_split= 2, n_estimators= 200),
        'gaussian': GaussianProcessRegressor(alpha= 0, kernel= 1**2 * RBF(length_scale=1e+03) + WhiteKernel(noise_level=0.001))
    }

    for name, mod in models.items():

        model = mod
        model.fit(X_train_values, y_train_values)
        # y_train_pred = model.predict(X_train_values).reshape(-1, 1)
        y_test_pred = model.predict(X_test_values).reshape(-1, 1)

        results[name] = y_test_pred
    
    return results