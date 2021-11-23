library(splines)
library(Epi)

num_rows <- 5
col_names <- c(
    "city", "years", "months", "exposure", "interactive",
    "outcome", "quantile", "lag", "iqr", "rr", "cil", "ciu", "B", "se"
)

results <- as.data.frame(matrix(nrow = num_rows, ncol = length(col_names)))
colnames(results) <- col_names

model1 <- glm(
    equation1, data = data, family = quasipoisson, na.action(na.omit))
model2 <- glm(
    equation2, data = data, family = quasipoisson, na.action(na.omit))

years <- paste(start_year, "-", end_year, sep = "")
months <- paste(start_month, "-", end_month, sep = "")

results[, 1] <- rep(city, each = num_rows)
results[, 2] <- rep(years, each = num_rows)
results[, 3] <- rep(months, each = num_rows)
results[, 4] <- rep(exposure, each = num_rows)
results[, 5] <- rep(interactive, each = num_rows)
results[, 6] <- rep(outcome, each = num_rows)
results[, 7] <- c(0:4)
results[, 8] <- rep(current_lag, each = num_rows)
results[, 9] <- rep(iqr, each = num_rows)
results[, 10:12] <- rbind(
    ci.exp(model1, subset = exposure),
    ci.exp(model2, subset = exposure)
)

sum1 <- summary(model1)$coefficients
sum2 <- summary(model2)$coefficients
exposure1 <- paste(exposure, "_", current_lag, sep = "")
exposure2 <- paste(
    exposure1, ":factor(", interactive, "_", current_lag, ")",
    sep = ""
)

results[, 13] <- c(
    sum1[exposure1, 1],
    sum2[exposure1, 1],
    sum2[paste0(exposure2, 1), 1],
    sum2[paste0(exposure2, 2), 1],
    sum2[paste0(exposure2, 3), 1]
)
results[, 14] <- c(
    sum1[exposure1, 2],
    sum2[exposure1, 2],
    sum2[paste0(exposure2, 1), 2],
    sum2[paste0(exposure2, 2), 2],
    sum2[paste0(exposure2, 3), 2]
)
