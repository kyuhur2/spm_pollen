from typing import List
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

import rpy2.robjects as robjects


# download r packages
utils = importr('utils')
utils.install_packages("Epi", repos="https://cloud.r-project.org")


class ModelGLM():
    def __init__(
        self,
        city: str,
        # num_lags: int,
        # moving_average: int,
        start_year: int,
        end_year: int,
        start_month: int,
        end_month: int,
        outcome: str,
        exposure: str,
        interactive: str,
        confounding: List[str],
        temp_bool: bool,
        temp_moving_average: int,
        current_lag_ma: int
    ):
        self.city = city
        # self.num_lags = num_lags
        # self.moving_average = moving_average
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.outcome = outcome
        self.exposure = exposure
        self.interactive = interactive
        self.confounding = confounding
        self.temp_bool = temp_bool
        self.temp_moving_average = temp_moving_average
        self.current_lag_ma = current_lag_ma

    def eq_creator(self):
        for i, i_element in enumerate(self.confounding):
            if i_element == "Tave":
                i_element = f"ns({i_element}, df=5)"

            if i_element == f"Tave_ma{self.current_lag_ma}":
                i_element = f"ns({i_element}, df=5)"

            if i_element == "doy":
                i_element = f"ns({i_element}, df=5):factor(year)"

            if (i_element == "dow") | (i_element == "holiday"):
                i_element = f"factor({i_element})"

            if i == 0:
                x = i_element

            else:
                x = x + " + " + i_element

        # non-interactive
        eq1 = (
            f"{self.outcome} ~ {self.exposure}_{self.current_lag_ma} + " +
            f"{self.exposure}_{self.current_lag_ma} + {x}"
        )

        # interactive
        eq2 = (
            f"{self.outcome} ~ {self.exposure}_{self.current_lag_ma}" +
            f":factor({self.interactive}_{self.current_lag_ma}) + " +
            f"{self.exposure}_{self.current_lag_ma} + {x}"
        )

        return eq1, eq2

    def r_glm(self, data):
        eq1, eq2 = self.eq_creator()

        pandas2ri.activate()
        robjects.globalenv["data"] = pandas2ri.py2ri(data)
        robjects.globalenv["equation1"] = eq1
        robjects.globalenv["equation2"] = eq2
        robjects.globalenv["city"] = self.city
        robjects.globalenv["exposure"] = self.exposure
        robjects.globalenv["outcome"] = self.outcome
        robjects.globalenv["interactive"] = self.interactive
        robjects.globalenv["current_lag"] = self.current_lag_ma
        robjects.r('''
            library(splines)
            library(Epi)

            results <- as.data.frame(matrix(nrow=5, ncol=10))
            colnames(results) <- c(
                "city", "exposure", "outcome", "quantile", "lag",
                "rr", "cil", "ciu", "B", "se"
            )

            model1 <- glm(
                equation1, data=data, family=quasipoisson, na.action(na.omit))
            model2 <- glm(
                equation2, data=data, family=quasipoisson, na.action(na.omit))

            results[, 1] <- rep(city, each=5)
            results[, 2] <- rep(exposure, each=5)
            results[, 3] <- rep(outcome, each=5)
            results[, 4] <- c(0:4)
            results[, 5] <- rep(current_lag, each=5)
            results[, 6:8] <- rbind(
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

            results[, 9] <- c(
                sum1[exposure1, 1],
                sum2[exposure1, 1],
                sum2[paste0(exposure2, 1), 1],
                sum2[paste0(exposure2, 2), 1],
                sum2[paste0(exposure2, 3), 1]
            )
            results[, 10] <- c(
                sum1[exposure1, 2],
                sum2[exposure1, 2],
                sum2[paste0(exposure2, 1), 2],
                sum2[paste0(exposure2, 2), 2],
                sum2[paste0(exposure2, 3), 2]
            )
        ''')
        results = robjects.globalenv["results"]
        print(results)

        return results
