library(splines)  # included in r-base


# run models
model1 <- glm(
    equation1, data = data, family = quasipoisson, na.action(na.omit))

exp1 <- as.data.frame(Epi::ci.exp(model1, subset = exposure))
sum1 <- as.data.frame(summary(model1)$coefficients)
exp1 <- tibble::rownames_to_column(exp1, "None")
sum1 <- tibble::rownames_to_column(sum1, "None")

if (interactive != "") {
    model2 <- glm(
        equation2, data = data, family = quasipoisson, na.action(na.omit))
    exp2 <- as.data.frame(Epi::ci.exp(model2, subset = exposure))
    sum2 <- as.data.frame(summary(model2)$coefficients)
    exp2 <- tibble::rownames_to_column(exp2, "None")
    sum2 <- tibble::rownames_to_column(sum2, "None")
}
