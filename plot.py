import matplotlib.pyplot as plt


def plotData(arr):
	plt.plot([i for i in range(len(arr))], arr)
	plt.xticks([])
	plt.yticks([])
	plt.savefig("data.png")


plotData([1, 4, 5])
