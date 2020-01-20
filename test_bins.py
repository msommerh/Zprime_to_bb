import numpy as np

def extend_binning(n, binning):\

    new_binning = []

    for i, lower_edge in enumerate(binning[:-1]):
        temp = np.linspace(binning[i], binning[i+1], n)

        if i!=0: temp = temp[1:]
        for entry in temp:
            new_binning.append(int(np.ceil(entry)))

    print "Now you have {} bins.".format(len(new_binning))
    return new_binning

dijet_bins = [1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067]

dijet_bins_17 = extend_binning(17, dijet_bins)
dijet_bins_5 = extend_binning(5, dijet_bins)
dijet_bins_10 = extend_binning(10, dijet_bins)
dijet_bins_15 = extend_binning(15, dijet_bins)
dijet_bins_20 = extend_binning(20, dijet_bins)
