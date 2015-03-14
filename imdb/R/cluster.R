library(RMySQL)
con <- dbConnect(MySQL(), user="orges", password="12345", dbname="empfehlung",host="localhost")
x <- dbGetQuery(con, "select group_concat(x) from weight_vector group by time;")
X <- matrix(as.numeric(unlist(strsplit((x[,1]),","))),byrow=TRUE,nrow=dim(x)[1])
mydata <- X
fit <- princomp(mydata, cor=TRUE)
summary(fit) # print variance accounted for
loadings(fit) # pc loadings
plot(fit,type="lines") # scree plot
fit$scores # the principal components
biplot(fit) 
