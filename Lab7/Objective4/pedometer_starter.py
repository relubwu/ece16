from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.metrics import accuracy_score
import numpy as np
from Libraries.ListBuffer import ListBuffer
import matplotlib.pyplot as plt


class Pedometer:

    # initial_steps is useful if you ever have to restart the pedometer
    def __init__(self, train_file_active, train_file_inactive, window_length=100, initial_steps=0):
        self.window_length = window_length
        self.steps = initial_steps
        self.knn = self.train(train_file_active, train_file_inactive)

        
    def extract_features(self, t, imu):
        # Split into 10 chunks
        length = int(np.size(imu)/10)
        imu = imu[0 : length * 10]
        imu = np.reshape(imu,(10, -1))
        #print(np.shape(imu))
        # Get the maxima of each chunk. The list comprehension is equivalent to a for-loop but cleaner!
        maxs = np.amax(imu, axis=1)
        # Return the average of these maxima
        result = np.mean(maxs)

        return result

    
    def train(self, train_file_active, train_file_inactive):
        """
        ---------------------- DATA LOADING ----------------------
        """
        # Load the data into numpy arrays. The data must only have two columns. Skip the labels row.
        t_active, data_active = np.loadtxt(train_file_active, delimiter=",", skiprows=1, usecols=(0,2),unpack=True)
        t_inactive, data_inactive = np.loadtxt(train_file_inactive, delimiter=",", skiprows=1, usecols=(0,2), unpack=True)
        

        # Reshape training data to be a 2D array
        t_active = np.array([t_active]).reshape(-1, 1)
        data_active = np.array([data_active]).reshape(-1, 1)
        t_inactive = np.array([t_inactive]).reshape(-1, 1)
        data_inactive = np.array([data_inactive]).reshape(-1, 1)

        
        

        # For both the active data and the inactive data, split it into windows of size window_length
        # Let's assume there are "num_window" windows

        # Slice
        offset = 0
        data_active_features = []
        while offset < np.size(data_active):
            data_active_s = data_active[offset: offset + 100]
            t_active_s = t_active[offset: offset + 100]
            offset+= 100
            
           # print(f)


            # Convert to numpy arrays, as required by sklearn.mixture.GaussianMixture
            # Extract features for each of these windows for both the active and active set
            # Do this by calling self.extract_features()
            # The result will be an array of num_window features for the active set, and a similar array for the inactive set
            data_active_features.append(self.extract_features( t_active_s, data_active_s))

        
            
        data_inactive_features = []
        # Slice
        offset = 0
        while offset < np.size(data_inactive):
            data_inactive_s = data_inactive[offset: offset + 100]
            t_inactive_s = t_inactive[offset: offset + 100]
            offset+= 100
            # Convert to numpy arrays, as required by sklearn.mixture.GaussianMixture

            # Extract features for each of these windows for both the active and active set
            # Do this by calling self.extract_features()
            # The result will be an array of num_window features for the active set, and a similar array for the inactive set
            data_inactive_features.append(self.extract_features(t_inactive_s, data_inactive_s)) 

        data_active_features = np.array(data_active_features).reshape(-1, 1)  
        data_inactive_features = np.array(data_inactive_features).reshape(-1, 1)
        

    
        # For both the active and the inactive set, split the features 50/50 into a training set and a validation set
        # The result will be an array of num_window//2 features for the active training set,
        # num_window//2 features for the active validation set, and something similar for the inactive set
        

                
        data_active_features_training = data_active_features [0 : int(np.size(data_active_features) / 2)]
        data_active_features_validation = data_active_features [int(np.size(data_active_features) / 2):]
        
        
        label_active_features_training = np.ones((np.size(data_active_features_training),), dtype=np.int)
        label_active_features_validation = np.ones((np.size(data_active_features_validation),), dtype=np.int)
        
        
        
        
        data_inactive_features_training = data_inactive_features [0 : int(np.size(data_inactive_features) / 2)]
        data_inactive_features_validation = data_inactive_features [int(np.size(data_inactive_features) / 2):]
        
        
        label_inactive_features_training = np.zeros((np.size(data_inactive_features_training),), dtype=np.int)
        label_inactive_features_validation = np.zeros((np.size(data_inactive_features_validation),), dtype=np.int)

        

        """
        ---------------------- TRAINING ----------------------
        """

        # Create training data
        # (1) Merge your array of features for the active training set and the inactive training set into one array.
        #     Reshape to a 2D array (of many rows and 1 column). Let's call this array X.
        # (2) Create the correct labels for these features in a separate array Y. It will have the same dimensions as X.
        #     When the data came from the actve set, the corresponding label should 0. When it came from the inactive set, the
        #     corresponding label should be 1.
 
        X = np.concatenate((data_active_features_training, data_inactive_features_training))
        Y = np.concatenate((label_active_features_training, label_inactive_features_training))
        

        
        
        
        data_active_features = np.array([data_active_features]).reshape(-1, 1)  
        data_inactive_features = np.array([data_inactive_features]).reshape(-1, 1)
        
        
        #print(X)
        #print("______________________________________________________")
        # Instantiate KNN
        knn = KNN(n_neighbors=3)

        # Train the KNN with X and Y
        knn.fit(X, Y)

        """
        ---------------------- VALIDATION ----------------------
        """

        # Create the validation data in a similar way as was done with the training data.
        # This will result in an array X_val and Y_val, with the data and labels respectively.
        X_val = np.concatenate((data_active_features_validation, data_inactive_features_validation))
        Y_val = np.concatenate((label_active_features_validation, label_inactive_features_validation))
        # Run KNN to predict the labels for validation data
        Y_predicted = knn.predict(X_val)
        
        # Find the accuracy by comparing Y_val with Y_predicted
        
        accuracy = accuracy_score(Y_val, Y_predicted)
        # Print the accuracy to the terminal

        print(accuracy)

        # Return he KNN parameters
        return knn

          
    def process(self, t_data, imu_data):
         # Return if we don't have enough data yet or were not given enough data
         if len(t_data) < self.window_length:
            return self.steps
         
        # Slice into just one window
         t = t_data[-self.window_length:]
         imu = imu_data[-self.window_length:]
    
        # Use the KNN to determine if the instantaneous state is active or inactive
        # call self.is_active(...)
         if self.is_active(t, imu):
    
        # Implement your own step counter heuristic
        # You can create new functions if you want
        
             try:
                self.steps += self.imu_heuristics(t, imu)
             except:
                return None
        
         return self.steps
     
    def is_active(self, t, imu):
    
         # Extract features for KNN
         # call self.extract_features(...)
         feature = self.extract_features(self, t, imu)
                
         # Classify using KNN
         result = self.knn.predict(feature)
                
         # Return the result (labels) of the classification
         return result
     
        
        
        
        
    def imu_heuristics(self, t, imu):
        
        
        


        return steps

