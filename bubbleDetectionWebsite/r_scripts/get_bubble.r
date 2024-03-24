library(ggplot2) # To handle plots
library(knitr) # for nice looking tables
library(tibble)

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
    stop("File path not provided.")
}

filename <- args[1]

# btc <- as_tibble(read.csv(file = "data/BTC_2023_2024.csv"))
btc <- as_tibble(read.csv(file = paste0("data/", args[1], ".csv")))
btc$date <- as.POSIXct(btc$open_time, format = "%m/%d/%Y %H:%M", origin = "1970-01-01")
y <- btc$open
obs <- length(y)
r0 <- 0.01 + 1.8 / sqrt(obs)
swindow0 <- floor(r0 * obs)

# saveRDS(ind95, file = "ind95.RDS")
index <- readRDS(paste0("data/ind95/", args[1], ".RDS"))

monitorDates <- btc$date[swindow0:obs]
maxi <- max(index)
lc <- which.max(index)

if (maxi == 1) { # there is at least one episode
    count <- 1
    EP <- matrix(0, nrow = 30, ncol = 2)
    # maximum 20 episodes: col1 origination date col2 termination date
    i <- lc + 1
    # print(monitorDates[lc])
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
    v <- nrow(OT)
    if (OT[v, 2] == 0 && !any(is.na(OT))) {
        OT[v, 2] <- monitorDates[length(monitorDates)]
    }
    # elif (OT)
    OT <- as.POSIXct(OT, origin = "1970-01-01")
    # typeof(OT)
    # "double"
} else if (maxi == 0) {
    OT <- NULL
    warning("No bubble or crisis periods found", call. = FALSE)
}
if (length(OT) == 0) {
    stop("No bubble or crisis periods found.", call. = FALSE)
}
if (!is.null(OT) && !any(is.na(OT))) {
    v <- nrow(OT)
    dateStamps <- data.frame(start = NULL, end = NULL)
    rN <- sample(1:obs, v, replace = TRUE)
    for (j in 1:v) {
        if (OT[j, 1] == OT[j, 2]) {
            newEntry <- data.frame(
                start = OT[j, 1],
                end = OT[j, 1]
            )
            dateStamps <- rbind(dateStamps, newEntry)
        } else {
            newEntry <- data.frame(
                start = OT[j, 1],
                end = OT[j, 2]
            )
            dateStamps <- rbind(dateStamps, newEntry)
        }
    }
    # print(dateStamps)
    bubbleDates <- dateStamps
    saveRDS(bubbleDates, file = paste0("data/bubble/", args[1], ".RDS"))
    kable(bubbleDates, caption = "Bubble and Crisis Periods in the BTC")

    start_time <- format(min(btc$date), "%Y-%m")
    end_time <- format(max(btc$date), "%Y-%m")

    ggp <- ggplot() +
        geom_rect(data = bubbleDates, aes(
            xmin = start, xmax = end,
            ymin = -Inf, ymax = Inf
        ), alpha = 0.5) +
        geom_line(data = btc, aes(date, price)) +
        #   scale_x_date(date_labels = "%m/%d/%Y") +
        labs(
            title = "Figure 2: BTC Price",
            subtitle = paste(start_time, end_time),
            caption = "Notes: The solid
line is the BTC price and the shaded areas are the periods where
the PSY statistic exceeds its 95% bootstrapped critical value.",
            x = "Year", y = "Price"
        )
    # print(ggp)
    print("ok")
} else {
    stop("No bubble")
}
