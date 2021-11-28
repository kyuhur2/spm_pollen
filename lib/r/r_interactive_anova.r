library(splines)  # included in r-base


# change model list to individual elements

anova1 <- stats::anova(model1s, test = "F")
anova2 <- stats::anova(model2s, test = "F")
