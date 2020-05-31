import numpy as np

def hampel_filter_pandas(input_series, window_size, n_sigmas):
    print("hampel_filter_pandas()", end="")
    input_series_np = input_series.values
    
    k = 1.4826 # scale factor for Gaussian distribution
    new_series = input_series.copy()

    # helper lambda function 
    MAD = lambda x: np.median(np.abs(x - np.average(x)))   # np.median(x)))
    
    rolling_median = input_series.rolling(window=2*window_size, center=True).median()
    rolling_mad = k * input_series.rolling(window=2*window_size, center=True).apply(MAD, raw=False)
    diff = np.abs(input_series - rolling_median)
    
    
    ind = np.where(diff > (n_sigmas * rolling_mad))
    inds = list(ind[0])
    
    orig_num_datapoints = input_series.shape[0]
    num_outliers = len(inds)
    
    outliers = np.empty((orig_num_datapoints))
    outliers[:] = np.nan #Makes array outlier the shape of original dataset with all elements = np.nan
    outliers[inds] = input_series[inds] #Fills in the array with the outlier data
    
    
    indicies_of_non_outliers = np.arange(orig_num_datapoints)
    indicies_of_non_outliers = np.delete(indicies_of_non_outliers, inds)
    
    non_outliers = np.empty((orig_num_datapoints))
    non_outliers[:] = np.nan
    non_outliers[indicies_of_non_outliers] = input_series[indicies_of_non_outliers]
    
    #mask = np.isnan(outliers) #Returns the boolean array mask for the new data, not including outliers
    
    #non_outliers = np.delete(input_series, inds)  Returns a np array with just non_outlier data. Outliars are skipped.
    print(" done!")
    print("found "+str(num_outliers)+" outliers and "+str(len(indicies_of_non_outliers))+" datapoints")
    return non_outliers,outliers