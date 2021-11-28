library(splines)  # included in r-base


# run models
model1 <- glm(
    equation1, data = data, family = quasipoisson, na.action(na.omit))
exp1 <- as.data.frame(Epi::ci.exp(model1, subset = exposure))
sum1 <- as.data.frame(summary(model1)$coefficients)

if (interactive != "") {
    model2 <- glm(
        equation2, data = data, family = quasipoisson, na.action(na.omit))
    exp2 <- as.data.frame(Epi::ci.exp(model2, subset = exposure))
    sum2 <- as.data.frame(summary(model2)$coefficients)
}
