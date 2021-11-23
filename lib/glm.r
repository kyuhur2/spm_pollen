library(splines)
library(Epi)

results <- as.data.frame(matrix(nrow=5, ncol=13))
colnames(results) <- c(
    "city", "years", "months", "exposure", "interactive",
    "outcome", "quantile", "lag", "rr", "cil", "ciu", "B", "se"
)

model1 <- glm(
    equation1, data=data, family=quasipoisson, na.action(na.omit))
model2 <- glm(
    equation2, data=data, family=quasipoisson, na.action(na.omit))

years <- paste(start_year, "-", end_year, sep="")
months <- paste(start_month, "-", end_month, sep="")

results[, 1] <- rep(city, each=5)
results[, 2] <- rep(years, each=5)
results[, 3] <- rep(months, each=5)
results[, 4] <- rep(exposure, each=5)
results[, 5] <- rep(interactive, each=5)
results[, 6] <- rep(outcome, each=5)
results[, 7] <- c(0:4)
results[, 8] <- rep(current_lag, each=5)
results[, 9:11] <- rbind(
    ci.exp(model1, subset=exposure),
    ci.exp(model2, subset=exposure)
)

sum1 <- summary(model1)$coefficients
sum2 <- summary(model2)$coefficients
exposure1 <- paste(exposure, "_", current_lag, sep="")
exposure2 <- paste(
    exposure1, ":factor(", interactive, "_", current_lag, ")",
    sep="")
print(sum1[exposure1, 1])

results[, 12] <- c(
    sum1[exposure1, 1],
    sum2[exposure1, 1],
    sum2[paste0(exposure2, 1), 1],
    sum2[paste0(exposure2, 2), 1],
    sum2[paste0(exposure2, 3), 1]
)
results[, 13] <- c(
    sum1[exposure1, 2],
    sum2[exposure1, 2],
    sum2[paste0(exposure2, 1), 2],
    sum2[paste0(exposure2, 2), 2],
    sum2[paste0(exposure2, 3), 2]
)
