library(ggplot2)
path <- "/Users/bailly/GARDEN/transition_model/results/log1.csv"
df <- read.csv(path, header=TRUE, sep=";")

#print frequency
g <- ggplot(df, aes(stimulus)) + geom_bar() + coord_flip()
#plot(g)
ggsave("/Users/bailly/GARDEN/transition_model/graphs/frequency.pdf")

#time 
g <- ggplot(df, aes(x=trial, y=time) )
g <- g + geom_point( aes(colour = factor(strategy)  )  )
g <- g + scale_color_manual(breaks = c("menu", "hotkey", "learning"), values=c("blue", "purple","green"))
plot(g)
ggsave("/Users/bailly/GARDEN/transition_model/graphs/time.pdf")
