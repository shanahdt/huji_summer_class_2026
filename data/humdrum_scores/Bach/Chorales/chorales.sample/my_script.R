setwd("~/corpora/humdrum_scores/Bach/Chorales/chorales.sample/")
my_data <- read.table("my_data.tsv", header =T)
str(my_data)
chorale <- cbind(my_data$file, my_data$part, my_data$entropy, 
                 my_data$npvi, my_data$meter, my)
 
library(corrplot)
corrplot(my_data)
M<-cor(my_data)
corrplot(M, method="circle")