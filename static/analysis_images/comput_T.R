x = c(3.6, 3.6, 3.7, 3.7, 3.6, 3.5, 3.75, 3.6, 3.5)

y <- c(3.3, 3.4, 3.4, 3.45, 3.45, 3.65)

Sp = ((length(x)-1)*(var(x))+ (length(y) - 1)*(var(y))) / (length(x) + length(y) - 2)

stand_error <- Sp * sqrt(1/length(x) + 1/length(y))

deltaT1 = qt(0.975, df = length(x) + length(y) - 2) * stand_error