from numpy import *def loadDataSet(df):	numFeat = df.values.shape[1] - 1	print "feature is ", numFeat	dataMat = []; labelMat = []	for line in df.values:		lineArr = []		for i in range(numFeat):			lineArr.append(float(line[i]))		dataMat.append(lineArr)		labelMat.append(float(line[-1]))	return dataMat, labelMat		def standRegres(xArr, yArr):	xMat = mat(xArr); yMat = mat(yArr).T	xTx = xMat.T * xMat	if linalg.det(xTx) == 0.0:		print "This matrix is singular, cannot do inverse"		return	ws = xTx.I * (xMat.T * yMat)	return ws		def lwlr(testPoint, xArr, yArr, k = 1.0):	xMat = mat(xArr); yMat = mat(yArr).T	m = shape(xMat)[0]	weights = mat(eye((m)))	for j in range(m):		diffMat = testPoint - xMat[j,:]		weights[j, j] = exp(diffMat * diffMat.T/(-2.0 * k ** 2))	xTx = xMat.T * (weights * xMat)	if linalg.det(xTx) == 0.0:		print "This matrix is singular, cannot do inverse"		return 	ws = xTx.I * (xMat.T * (weights * yMat))	return testPoint * ws			def lwlrTest(testArr, xArr, yArr, k = 1.0):	m = shape(testArr)[0]	yHat = zeros(m)	for i in range(m):		yHat[i] = lwlr(testArr[i], xArr, yArr, k)	return yHat	def Wlwlr(testPoint, xArr, yArr, wArr, k = 1.0):	xMat = mat(xArr); yMat = mat(yArr).T;	m = shape(xMat)[0]	weights = mat(eye((m)))	for j in range(m):		diffMat = testPoint - xMat[j,:]		#weights[j, j] = 100 ** wArr[j]		weights[j, j] = exp(((diffMat * diffMat.T/(-2.0 * k ** 2)) * wArr[j])) 		#print type(weights)		#print type(wMat[j, :])		#weights[j, j] *= wMat[j, :].flatten().A[0]	xTx = xMat.T * (weights * xMat)	if linalg.det(xTx) == 0.0:		print "This matrix is singular, cannot do inverse"		return 	ws = xTx.I * (xMat.T * (weights * yMat))	return testPoint * ws			def WlwlrTest(testArr, xArr, yArr, wArr, k = 1.0):	m = shape(testArr)[0]	yHat = zeros(m)	for i in range(m):		yHat[i] = Wlwlr(testArr[i], xArr, yArr, wArr, k)	return yHat	def ressError(yArr, yHatArr):	return ((yArr - yHatArr) ** 2).sum()	