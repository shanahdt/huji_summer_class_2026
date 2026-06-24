library(dplyr)
tibble_result <- tibble(
  pitch = pitch(freygish_1$Token),
  duration = dur(freygish_1$Token)
)
tibble_result
tibble_result$duration <- as.numeric(tibble_result$duration)
tibble_result$pitch <- as.factor(tibble_result$pitch)

duration <- tibble_result |> 
    group_by(pitch) |>
    summarise(by_duration = sum(duration))


ggplot(duration, aes(x=pitch, y=by_duration)) +
    geom_bar(stat="identity") + theme_bw() +
    labs(y="count weighted by duration") +
    theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1))



mode <- c("Freygish", "Raised fourth", "Minor", "Major")
number <- c(71, 34, 106, 43)
df <- data.frame(
        mode = c("Freygish", "Raised fourth", "Minor", "Major"), 
        number = c(71, 34, 106, 43))
ggplot(df, aes(x=mode, y=number)) +
   geom_bar(stat="identity") + theme_bw() +
    labs(y="Mode") +
    theme(axis.text.x = element_text(size = 16, angle = 90, vjust = 0.5, hjust=1),
          axis.text.y = element_text(size=16)) +
    labs(title = "Prevalence of Modes in Beregovski's Instrumental Volume")



set.seed(1)

age <- factor(sample(c("Child", "Adult", "Retired"),
              size = 50, replace = TRUE),
              levels = c("Child", "Adult", "Retired"))
hours <- sample(1:4, size = 50, replace = TRUE)
city <- sample(c("A", "B", "C"),
               size = 50, replace = TRUE)

df <- data.frame(x = age, y = hours, group = city)    


mode <- c("All", "Freygish", "Raised fourth", "Minor", "Major", "All", "Freygish", "Raised fourth", "Minor", "Major")
counts <- c(115, 36, 17, 44, 18, 134, 32, 16, 61, 25)
modulation <- c("Modulation", "Modulation", "Modulation", "Modulation", "Modulation", 
                "No modulation", "No modulation", "No modulation", "No modulation", "No modulation")

df <- data.frame(x = mode, y = counts, group = modulation)              



ggplot(df, aes(x = x, y = counts, fill = group)) +
  geom_bar(stat = "identity") +
    labs(y="Mode") +
    theme(axis.text.x = element_text(size = 16, 
                angle = 90, vjust = 0.5, hjust=1),
          axis.text.y = element_text(size=16)) +
    theme_bw() +
    labs(title = "Modulation percentages by mode") +
    guides(fill = guide_legend(title = "Modulation")) +
    scale_fill_manual(values = c("gray40", "gray70"))