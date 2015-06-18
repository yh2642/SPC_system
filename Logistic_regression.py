from numpy import *import randomdef loadDataSet(df):	numFeat = df.values.shape[1] - 1	print "feature is ", numFeat	dataMat = []; labelMat = []	for line in df.values:		lineArr = []		for i in range(numFeat):			lineArr.append(float(line[i]))		dataMat.append(lineArr)		labelMat.append(float(line[-1]))	return dataMat, labelMat	def sigmoid(inX):	return 1.0 / (1 + exp(-inX))	def gradAscent(dataMatIn, classLabels):	dataMatrix = mat(dataMatIn)	labelMat = mat(classLabels).transpose()	m, n = shape(dataMatrix)	alpha = 0.01	maxCycles = 10000	weights = ones((n, 1))	for k in range(maxCycles):		h = sigmoid(dataMatrix * weights)		error = (labelMat - h)		weights = weights + alpha * dataMatrix.transpose() * error	return weightsdef stocGradAscent1(dataMatrix, classLabels, feature_mean, numIter = 150):	m, n = shape(dataMatrix)	weights = ones(n)	for j in range(numIter):		dataIndex = range(m)		for i in range(m):			alpha = 4 / (1.0 + j + i) +0.1			randIndex = int(random.uniform(0, len(dataIndex)))			h = sigmoid(sum(dataMatrix[randIndex] * weights))			error = classLabels[randIndex] - h			weights = weights + alpha * error * dataMatrix[randIndex] * feature_mean			del(dataIndex[randIndex])	return weights	def classifyVector(inX, weights):	prob = sigmoid(sum(inX * weights))	print prob	if prob > 0.5: return 1.0	else: return 0	def mtTest(tspc1, mspc1):	col= [        'Rsd3_dist', 'Rsd4_dist', 'err2', 'err3', 'err6', 'zone3_dist',       'zone4_dist', 'reason_step', 'label'] 	tspc1['label'] = 1.0	mspc1['label'] = 0	       	data_t = tspc1.reindex(columns = col)	data_m = mspc1.reindex(columns = col)	xArr_t, yArr_t = loadDataSet(data_t)	xArr_m, yArr_m = loadDataSet(data_m)		n = 85	trainingSet = []; trainingLabels = []; testingSet = []; testingLabels = []	indx_pool = range(len(xArr_t))	while n > 0:		rand_indx = random.choice(indx_pool)		trainingSet.append(xArr_t[rand_indx])		trainingLabels.append(yArr_t[rand_indx])		indx_pool.remove(rand_indx)		n -= 1	#for indx in indx_pool:		#testingSet.append(xArr_t[indx])		#testingLabels.append(yArr_t[indx])	n = 20	while n > 0:		rand_indx = random.choice(indx_pool)		testingSet.append(xArr_t[rand_indx])		testingLabels.append(yArr_t[rand_indx])		indx_pool.remove(rand_indx)		n -= 1		n = 85	indx_pool = range(len(xArr_m))	while n > 0:				rand_indx = random.choice(indx_pool)		trainingSet.append(xArr_m[rand_indx])		trainingLabels.append(yArr_m[rand_indx])		indx_pool.remove(rand_indx)		n -= 1		for indx in indx_pool:		testingSet.append(xArr_m[indx])		testingLabels.append(yArr_m[indx])		print "the length of training set is ", len(trainingSet)	print "the length of testing set is ", len(testingSet)		feature_mean = array(trainingSet).mean(axis = 0)	trainWeights = stocGradAscent1(array(trainingSet), array(trainingLabels), feature_mean, 2000)	#trainWeights = gradAscent(array(trainingSet), array(trainingLabels))	print trainWeights############# start testing	errorCount = 0; numTestVec = 0.0	for indx in range(len(testingSet)):		if classifyVector(array(testingSet[indx]), trainWeights) != 	testingLabels[indx]:			errorCount += 1		#print classifyVector(array(testingSet[indx]), trainWeights), testingLabels[indx]	errorRate = float(errorCount) / len(testingLabels)	print testingLabels	print "the error rate of this test is: %f" % errorRate	return errorRate