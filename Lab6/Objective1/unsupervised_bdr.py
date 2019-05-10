# ---------------------------------------- Import Libraries ---------------------------------------- #
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sig
from sklearn.mixture import GaussianMixture as GM
import matplotlib.mlab as mlab

# ---------- Import Your Modules HERE ---------- #


if (__name__ == "__main__"):
    
    ##########
    # Step 1 #
    ##########
    # ---------- Load training data ---------- #
    # Load training data
    data_time_tr, data_ir_tr = np.loadtxt("ir_data_train.csv", delimiter=",", skiprows=1, unpack=True)

    
    ##########
    # Step 2 #
    ##########
    # ---------- Plot 5 sec of Raw Data ---------- #
    plt.figure()
    # PLOT HERE
    plt.show()

    
    ##########
    # Step 3 #
    ##########
    # ---------- Plot Histogram ---------- #
    # Plot the histogram of your training dataset, here.
    plt.figure()
    plt.hist(data_ir_tr, 50)
    plt.xlabel("IR reading")
    plt.ylabel("Count (#)")
    plt.title("IR Signal Histogram")
    

    ##########
    # Step 4 #
    ##########
    # ---------- Find GMM ---------- #
    # Create GMM object
    gmm = GM(n_components=2)

    # Fit 2 component Gaussian to the data
    gmm_fit = gmm.fit(np.array([data_time_tr, data_ir_tr]))              # Pass correct parameters. Remember that this expects a 2D array.

    # Retrieve Gaussian parameters
    mu0 = gmm_fit.means_[0]
    mu1 = gmm_fit.means_[1]
    sig0 = np.sqrt(gmm_fit.covariances_[0])
    sig1 = np.sqrt(gmm_fit.covariances_[1])
    w0 = gmm_fit.weights_[0]
    w1 = gmm_fit.weights_[1]

    # ---------- Plot Gaussians sum over histogram ---------- #
    # Create an "x" array from which to compute the Gaussians
    x = np.reshape((np.linspace(np.min(data_ir_tr), np.max(data_ir_tr), 1000)), [1000, 1])
    plt.figure()
    plt.hist(data_ir_tr, bins=50, density=True)
    plt.xlabel("IR reading")
    plt.ylabel("Count (#)")
    plt.title("IR Signal Histogram")
    plt.plot(x, w0 * mlab.normpdf(x, mu0, sig0) + w1 * mlab.normpdf(x, mu1, sig1))
        
    # ---------- Plot two Gaussians over histogram ---------- #
    # Add the appropriate code
        
        
    ##########
    # Step 5 #
    ##########
    # ---------- Load validation data ---------- #
    # Load validation data
    data_time_va, data_ir_va = np.loadtxt("path to ir_data_validation.csv", delimiter=",", skiprows=1, unpack=True)
        
    # ---------- Predict Labels for training data ---------- #
    # Predict training labels
    train_pred_lbl = gmm_fit.predict()                     # Pass correct parameters

    # ---------- Predict Labels for validation data ---------- #
    # Predict validation labels
    validation_pred_lbl = gmm_fit.predict()                # Pass correct parameters

    # ---------- Plot Training Set predictions ---------- #
    # Complete the code
        
    # ---------- Plot Validation Set predictions ---------- #
    # Complete the code
