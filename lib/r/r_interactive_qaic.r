library(splines)  # included in r-base


qaic <- function(model) {
    phi <- summary(model)$dispersion
    loglik <- sum(dpois(model$y, model$fitted.values, log=TRUE))
    return((-2 * loglik) + 2 * summary(model)$df[3] * phi)
}

# run models
model1 <- glm(
    equation1, data = data, family = quasipoisson, na.action(na.omit))
qaic1 <- qaic(model1)

if (interactive != "") {
    model2 <- glm(
        equation2, data = data, family = quasipoisson, na.action(na.omit))
    qaic2 <- qaic(model2)
}
