# Generate the bubble duration

library(psymonitor) # For testing for bubble monitoring
library(ggplot2) # To handle plots
library(knitr) # for nice looking tables
library(tibble)

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
    stop("File path not provided.")
}

# filename <- "BTC_2023_2024"

filename <- args[1]

csv_file <- paste0("data/", args[1], ".csv")

if (file.exists(csv_file)) {
    btc <- as_tibble(read.csv(file = csv_file))
} else {
    stop("CSV file not found: ", csv_file)
}

btc$date <- as.POSIXct(btc$open_time, format = "%m/%d/%Y %H:%M", origin = "1970-01-01")
# save_ind95 <- paste("scripts/output/", filename, ".RDS", sep = "")
save_ind95 <- paste0("data/ind95/", filename, ".RDS")

y <- btc$open
obs <- length(y)
# 907
r0 <- 0.01 + 1.8 / sqrt(obs)
# 0.06976802
# Windowsize
swindow0 <- floor(r0 * obs)
# 63
dim <- obs - swindow0 + 1
# 845
IC <- 2
adflag <- 6
yr <- 2
Tb <- 12 * yr + swindow0 - 1
# 86
nboot <- 99

bsadf <- PSY(y, swindow0, IC, adflag)
quantilesBsadf <- cvPSYwmboot(y, swindow0, IC, adflag, Tb, nboot, nCores = 2) # Note that the number of cores is arbitrarily set to 2.
quantile95 <- quantilesBsadf %*% matrix(1, nrow = 1, ncol = dim)
ind95 <- (bsadf > t(quantile95[2, ])) * 1
saveRDS(ind95, file = save_ind95)
index <- ind95
monitorDates <- btc$date[swindow0:obs]
bubbleDates <- NULL

# periods <- locate(ind95, monitorDates)
maxi <- max(index)
lc <- which.max(index)
if (maxi == 1) { # there is at least one episode
    count <- 1
    EP <- matrix(0, nrow = 30, ncol = 2)
    # maximum 20 episodes: col1 origination date col2 termination date
    i <- lc + 1
    EP[count, 1] <- monitorDates[lc]
    while (i <= length(index)) {
        if (index[i - 1] == 1 && index[i] == 0) {
            EP[count, 2] <- monitorDates[i - 1]
            i <- i + 1
        } else if (index[i - 1] == 0 && index[i] == 1) {
            count <- count + 1
            EP[count, 1] <- monitorDates[i]
            i <- i + 1
        } else {
            i <- i + 1
        }
    }
    OT <- EP[1:count, ]
    print(dim(OT))
    v <- nrow(OT)
    if (OT[v, 2] == 0 && !any(is.na(OT))) {
        OT[v, 2] <- monitorDates[length(monitorDates)]
    }
    OT <- as.POSIXct(OT, origin = "1970-01-01")
} else if (maxi == 0) {
    OT <- NULL
    warning("No bubble or crisis periods found", call. = FALSE)
    v <- 0
} else {
    # Only create bubbleDates when OT is not NULL
    bubbleDates <- data.frame(start = NULL, end = NULL)
    rN <- sample(1:obs, v, replace = TRUE)
    for (j in 1:v) {
        if (OT[j, 1] == OT[j, 2]) {
            newEntry <- data.frame(
                start = OT[j, 1],
                end = OT[j, 1]
            )
            bubbleDates <- rbind(bubbleDates, newEntry)
        } else {
            newEntry <- data.frame(
                start = OT[j, 1],
                end = OT[j, 2]
            )
            bubbleDates <- rbind(bubbleDates, newEntry)
        }
    }
}

# bubbleDates <- disp(periods, obs)
if (!is.null(bubbleDates)) {
    # save_bubbleDates <- "bubble_bubbleDates.RDS" # Define filename for saving bubbleDates
    save_bubbleDates <- paste0("data/bubble/", filename, "_bubble.RDS") # Define filename for saving bubbleDates
    saveRDS(bubbleDates, file = save_bubbleDates)
    kable(bubbleDates, caption = "Bubble and Crisis Periods in the BTC")

    start_time <- format(min(btc$date), "%Y-%m")
    end_time <- format(max(btc$date), "%Y-%m")

    ggp <- ggplot() +
        geom_rect(data = bubbleDates, aes(
            xmin = start, xmax = end,
            ymin = -Inf, ymax = Inf
        ), alpha = 0.5) +
        geom_line(data = btc, aes(date, price)) +
        labs(
            title = "Figure 2: BTC Price",
            subtitle = paste(start_time, end_time),
            caption = "Notes: The solid line is the BTC price and the shaded areas are the periods where the PSY statistic exceeds its 95% bootstrapped critical value.",
            x = "Year", y = "Price"
        )
    print(ggp)
} else {
    # save_bubbleDates <- "empty_bubbleDates.RDS" # Define filename for saving empty data frame
    save_bubbleDates <- paste("data/bubble/", "empty_bubbleDates", ".RDS") # Define filename for saving empty data frame
    empty_df <- data.frame(start = NULL, end = NULL)
    saveRDS(empty_df, file = save_bubbleDates)
}
saveRDS(bubbleDates, file = save_bubbleDates)
# kable(bubbleDates, caption = "Bubble and Crisis Periods in the BTC")

start_time <- format(min(btc$date), "%Y-%m")
end_time <- format(max(btc$date), "%Y-%m")

times <- data.frame(start_time, end_time)
write.csv(times, file = paste0("data/bubble/", filename, "_bubble.RDS"), row.names = FALSE)
