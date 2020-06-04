rm(list = ls())
library(ggplot2)
library(dplyr)
library(GGally)
library(reshape2)
library(cowplot)

exit
#######################
bar_plot_bic_technique_model <- function(df_original, path){
  df_max_user <- df_original %>% group_by(model_name, technique_name, n_params, N, user_id) %>% summarize(log_likelyhood = max(log_likelyhood)) %>% arrange(model_name, technique_name, log_likelyhood)
  df_max_user <-df_max_user %>% filter(model_name != "random")
  df_max_user$bic <- 0
  df_max_user$bic <- 2 * df_max_user$log_likelyhood + df_max_user$n_params * log(df_max_user$N)  #* df_max_user$N
  level_order <- c("RW", "RW_without", "CK", "RW_CK", "trans", "TRANS_D", "TRANS_DK0", "TRANS_DCK")
  df_max_user$model_name <- factor(df_max_user$model_name, levels = level_order)
  with( df_max_user, df_max_user[order(model_name) ] )
  View(df_max_user)
  
  g <- ggplot() 
  g <- g + geom_bar(data = df_max_user, aes(y = bic, x = user_id, group = factor(model_name, level_order) , fill = factor(model_name, level_order) ), stat="identity")#, position = "dodge")
  g <- g + facet_grid(technique_name ~ .)
  g <- g + ggtitle( "BIC per model, technique and user" ) + xlab("User") + ylab("Log likelyhood")
  plot(g)
  filename <- paste(path, "likelyhood_model_technique_users_2.pdf", sep="")
  ggsave( filename )
  
}


#############################
scatter_plot_likelyhood_hotkeycount_technique_model <- function(df_original, path){
  df_max_user <- df_original %>% group_by(model_name, technique_name, hotkey_count, user_id) %>% summarize(log_likelyhood = - max(log_likelyhood)) %>% arrange(model_name, technique_name, log_likelyhood)
  g <- ggplot() 
  g <- g + geom_jitter(data = df_max_user, width=25, height=25, alpha = 0.5, aes(y = log_likelyhood, x = hotkey_count, color=technique_name) )
  g <- g + facet_grid(. ~ model_name)
  g <- g + ggtitle( "Likelyhood per model, technique, hotkey count" )
  g <- g + xlab("Hotkey count") + ylab("log_likelyhood")
  plot(g)
  filename <- paste(path, "likelyhood_model_technique_hotkeycount.pdf", sep="")
  ggsave( filename)
}


##############################
distrib_params <- function(df, graph_path){
  g <- ggplot(df, aes(x=p1)) + geom_histogram(binwidth = 0.1, colour="black", fill="white")
  g <- g+ facet_grid(technique_name ~ model_name)
  g <- g + ggtitle( "P1 = b IF Random ELSE alpha" ) + xlab("Models") + ylab("Technique")
  plot(g)
  filename <- paste( graph_path, "distrib_p1.pdf", sep="")
  ggsave(filename)
  
  df <- df %>% filter(p2!=-1)
  g <- ggplot(df, aes(x=p2)) + geom_histogram(binwidth = 0.5, colour="black", fill="white")
  g <- g+ facet_grid(technique_name ~ model_name)
  g <- g + ggtitle( "P2 = beta" ) + xlab("Models") + ylab("Technique")
  plot(g)
  filename <- paste( graph_path, "distrib_p2.pdf", sep="")
  ggsave(filename)

  df <- df %>% filter(p3!=-1)
  g <- ggplot(df, aes(x=p3)) + geom_histogram(binwidth = 0.025, colour="black", fill="white")
  g <- g+ facet_grid(technique_name ~ model_name)
  g <- g + ggtitle( "P3 = alphaC" ) + xlab("Models") + ylab("Technique")
  plot(g)
  filename <- paste( graph_path, "distrib_p3.pdf", sep="")
  ggsave(filename)
  df <- df %>% filter(p4!=-1)
  g <- ggplot(df, aes(x=p4)) + geom_histogram(binwidth = 0.5, colour="black", fill="white")
  g <- g+ facet_grid(technique_name ~ model_name)
  g <- g + ggtitle( "P4 = betaC" ) + xlab("Models") + ylab("Technique")
  plot(g)
  filename <- paste( graph_path, "distrib_p4.pdf", sep="")
  ggsave(filename)
  
}


##############################
parallel_coord <- function(df_original, nb_param, graph_path) {
  df_user <- df_original %>% group_by(model_name, user_id) %>% filter(log_likelyhood == max(log_likelyhood) )
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p1 == min(p1)) #use to avoid doublons
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p2 == min(p2)) #use to avoid doublons
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p3 == min(p3)) #use to avoid doublons
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p4 == min(p4)) #use to avoid doublons
  df_user$hotkey_count <- df_user$hotkey_count / 10
  df_user$log_likelyhood <- - df_user$log_likelyhood / 100
  df_user$p1 <- df_user$p1 * 10
  
  threshold_adoption = 0
  df_user_no_hotkey <- df_user %>% filter( hotkey_count <= threshold_adoption)
  df_user_hotkey <- df_user %>% filter( hotkey_count > threshold_adoption)
  View(df_user_no_hotkey)
  
  ids = c("model_name", "user_id", "technique_name")
  measures = c("log_likelyhood", "p1", "p2", "p3", "p4", "p5")
  df_user_no_hotkey <- melt(data = df_user_no_hotkey, id= ids, measure.vars = measures)  
  df_user_hotkey <- melt(data = df_user_hotkey, id= ids, measure.vars = measures) 
  
  g <- ggplot(df_user_no_hotkey,alpha = 0.75, aes(x=variable,y=value,colour=as.factor(technique_name), group = user_id))
  g <- g + geom_line()+facet_grid(technique_name ~ model_name)
  g <- g + ggtitle( "Parallel coord per model and technique for NON-hotkey users" ) + xlab("Parameters") + ylab("Technique")
  plot(g)
  filename <- paste( graph_path, "parallel_corrd.pdf", sep="")
  ggsave(filename)
  
  g <- ggplot(df_user_hotkey,alpha = 0.75, aes(x=variable,y=value,colour=as.factor(technique_name), group = user_id))
  g <- g + geom_line()+facet_grid(technique_name ~ model_name)
  g <- g + ggtitle( "Parallel coord per model and technique for hotkey users" ) + xlab("Parameters") + ylab("Technique")
  plot(g)
  filename <- paste( graph_path, "parallel_corrd.pdf", sep="")
  ggsave(filename)
  
  #ggparcoord(df_user, columns=6:9, groupColumn=11, alphaLines = 0.3, scale="globalminmax")
}


#########################################################
#########################################################
best_params_users <- function(df_original, graph_path) {
  df_user <- df_original %>% group_by(model_name, user_id) %>% filter(log_likelyhood == max(log_likelyhood) )
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p1 == min(p1)) #use to avoid doublons
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p2 == min(p2)) #use to avoid doublons
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p3 == min(p3)) #use to avoid doublons
  df_user <- df_user %>% group_by(model_name, user_id) %>% filter(p4 == min(p4)) #use to avoid doublons
  return (df_user)
}


#########################################################
#########################################################
best_params_techniques <- function(df_original, graph_path) {
  #remove non-hotkey users
  df <- df_original %>% filter(hotkey_count != 0 )
  df <- df %>% group_by(model_name, technique_id, p1,p2,p3,p4) %>% summarize(log_likelyhood = mean(log_likelyhood) )
  View(df)
  df2 <- df %>% group_by(model_name, technique_id) %>% filter(log_likelyhood == max(log_likelyhood) )
  View(df2)

  return (df2)
}



#########################################################
#########################################################
analyze_one_param_model <- function(df_original, name, param_name, graph_path) {
  p <- paste( graph_path, name, sep="")
  dfi <- df_original[ grepl(name, df_original$model_name), ]
  df_p1 <- dfi %>% group_by(p1) %>% dplyr::summarize(log_likelyhood = mean(log_likelyhood), na.rm = TRUE )
  df_max <- df_p1 %>% filter(log_likelyhood == max(log_likelyhood) )
  df_user <- dfi %>% group_by(user_id) %>% dplyr::summarize(log_likelyhood = max(log_likelyhood), na.rm = TRUE )
  df_max_user <- dfi %>% group_by(user_id) %>% filter(log_likelyhood == max(log_likelyhood))
  df_max_user <- df_max_user %>% group_by(user_id) %>% filter(p1 == min(p1))
  df_max_user_tech <- df_max_user %>% group_by(technique_name) %>% count(p1)
  df_no_adoption <- df_max_user %>% filter(hotkey_count == 0 )
  df_no_adoption_count <-df_no_adoption %>% group_by(technique_name) %>% count(p1)
  df_user_print <<- df_no_adoption
  
  ################ one line for each user
  g <- ggplot(   )
  g <- g + geom_line(data = df_p1, aes(x=p1, y =log_likelyhood), size = 2)
  g <- g + geom_point(data = df_max, aes(x=p1, y= log_likelyhood), size = 5 )
  g <- g + geom_line( data=dfi, aes(x=p1, y=log_likelyhood, group = user_id, color = technique_name )  )
  g <- g + geom_jitter(data = df_max_user, size= 2, aes(x=p1, y= log_likelyhood, color = technique_name, shape = technique_name) )
  g <- g + geom_point(data = df_no_adoption, size = 6, shape=21, aes(x=p1, y = log_likelyhood))
  g <- g + ggtitle( paste("Model", name, sep= " " ) )
  g <- g + xlab( param_name )
  g <- g + ylab("Log likelyhood")
  plot(g)
  filename <- paste(p, "_param_space.pdf", sep="")
  ggsave(filename)
  
  
  ################ distribution parameter
  g <- ggplot() 
  g <- g + geom_bar(aes(y = n, x = p1, fill=technique_name), data = df_max_user_tech,stat="identity")
  g <- g + ggtitle( paste("Model", name, sep= " " ) ) + xlab(param_name) + ylab("Number of users")
  plot(g)
  filename <- paste(p, "_user_distrib.pdf" , sep="")
  ggsave( filename )
  
  ################## parameter value as a function of hotkey count
  g <- ggplot() 
  g <- g + geom_jitter(data = df_max_user, aes(y = p1, x = hotkey_count, color=technique_name) )
  g <- g + geom_point(data = df_no_adoption, size = 6, shape=21, aes(y=p1, x = hotkey_count))
  g <- g + ggtitle( paste("Model", name, sep= " " ) ) + xlab("hotkey count") + ylab(param_name)
  plot(g)
  filename <- paste(p, "_hotkey.pdf" , sep="")
  ggsave( filename )
  
}



##############################
analyze_two_param_model <- function(df_original, name, param_name, graph_path) {
  p <- paste( graph_path, name, sep="")
  dfi <- df_original[ grepl(name, df_original$model_name), ]
  df_p <- dfi %>% group_by(p1, p2) %>% dplyr::summarize(log_likelyhood = mean(log_likelyhood), na.rm = TRUE )
  df_user <- dfi %>% group_by(user_id) %>% filter(log_likelyhood == max(log_likelyhood) )
  df_user <- df_user %>% group_by(user_id) %>% filter(p1 == min(p1)) #use to avoid doublons
  df_user <- df_user %>% group_by(user_id) %>% filter(p2 == min(p2)) #use to avoid doublons
  df_no_adoption <- df_user %>% filter(hotkey_count == 0 )
  
  
  ################
  g<-ggplot(data = df_p, aes(x=p1, y=p2, fill=log_likelyhood))
  g <- g + geom_raster(interpolate = TRUE)
  g <- g + ggtitle("heat map log likelyhood as a function of parameters") + xlab( param_name[1] )+ ylab( param_name[2] )
  #g <- g + scale_color_gradientn(colours = rainbow(4))
  g <- g + scale_fill_continuous(type = "viridis")
  g <- g + geom_point(data = df_no_adoption, size = 6, fill = "white", shape=21, aes(x=p1, y = p2))
  g <- g + geom_jitter(data = df_user, size = 2, fill= "white", aes(x=df_user$p1, y=df_user$p2, shape = df_user$technique_name, color= df_user$technique_name), width = 0.01, height = 0.05)
  plot(g)
  filename <- paste(p, "_likelyhood_p.pdf", sep="")
  ggsave(filename)
  
  # ################
  g <- ggplot() 
  g <- g + geom_bar(data = df_user, aes(y = log_likelyhood, x = technique_name, group = as.factor(user_index), fill=technique_name), stat="identity", position = "dodge")
  g <- g + ggtitle( paste("Model", name, sep= " " ) )+ xlab(param_name) + ylab("Log likelyhood")
  plot(g)
  filename <- paste(p, "_users.pdf" , sep="")
  ggsave( filename )
  
  ##################
  g <- ggplot() 
  g <- g + geom_point(data = df_user, aes(y = p1, x = hotkey_count, color=technique_name) )
  g <- g + ggtitle( paste("Model", name, sep= " " ) )
  g <- g + xlab("hotkey count")
  g <- g + ylab(param_name[1])
  plot(g)
  filename <- paste(p, "_hotkey_p1.pdf" , sep="")
  ggsave( filename )
 
  ##################
  g <- ggplot() 
  g <- g + geom_point(data = df_user, aes(y = p2, x = hotkey_count, color=technique_name) )
  g <- g + ggtitle( paste("Model", name, sep= " " ) )
  g <- g + xlab("hotkey count")
  g <- g + ylab(param_name[2])
  plot(g)
  filename <- paste(p, "_hotkey_p2.pdf" , sep="")
  ggsave( filename )
}





###################################
all_likelyhood_per_param_model <- function(df, path){
  #df_max_user <- df_original %>% group_by(model_name, technique_name, hotkey_count, user_id) %>% summarize(log_likelyhood = - max(log_likelyhood)) %>% arrange(model_name, technique_name, log_likelyhood)
  g <- ggplot()
  g <- g + geom_point(data = df, alpha = 0.05, aes(y = log_likelyhood, x = p1) )
  g <- g + facet_grid(user_id ~ model_name)
  g <- g + ggtitle( "log Likelyhood per param, model" )
  g <- g + xlab("p1") + ylab("log_likelyhood")
  g <- g + ylim(-5000,0)
  plot(g)
  filename <- paste(path, "log_likelyhood_model_p1_.pdf", sep="")
  ggsave( filename)

  g <- ggplot()
  g <- g + geom_point(data = df, alpha = 0.05, aes(y = log_likelyhood, x = p2) )
  g <- g + facet_grid(user_id ~ model_name)
  g <- g + ggtitle( "log Likelyhood per param, model" )
  g <- g + xlab("p2") + ylab("log_likelyhood")
  g <- g + ylim(-1000,0)
  plot(g)
  filename <- paste(path, "log_likelyhood_model_p2_.pdf", sep="")
  ggsave( filename)

  g <- ggplot()
  g <- g + geom_point(data = df, alpha = 0.05, aes(y = log_likelyhood, x = p3) )
  g <- g + facet_grid(user_id ~ model_name)
  g <- g + ggtitle( "log Likelyhood per param, model" )
  g <- g + xlab("p3") + ylab("log_likelyhood")
  g <- g + ylim(-1000,0)
  plot(g)
  filename <- paste(path, "log_likelyhood_model_p3_.pdf", sep="")
  ggsave( filename)
  
  g <- ggplot() 
  ff <- df %>% filter(model_name == "RW_D" | model_name == "RW_IG")
  g <- g + geom_point(data = ff, alpha = 0.05, aes(y = log_likelyhood, x = p4) )
  g <- g + facet_grid(user_id ~ model_name)
  g <- g + ggtitle( "log Likelyhood per param, model" )
  g <- g + xlab("p4") + ylab("log_likelyhood")
  g <- g + ylim(-1000,0)
  plot(g)
  filename <- paste(path, "log_likelyhood_model_p4_.pdf", sep="")
  ggsave( filename)
  
  g <- ggplot()
  g <- g + geom_point(data = df, alpha = 0.05, aes(y = log_likelyhood, x = p5) )
  g <- g + facet_grid(user_id ~ model_name)
  g <- g + ggtitle( "log Likelyhood per param, model" )
  g <- g + xlab("p5") + ylab("log_likelyhood")
  g <- g + ylim(-1000,0)
  plot(g)
  filename <- paste(path, "log_likelyhood_model_p5_.pdf", sep="")
  ggsave( filename)
}


#######################
bar_plot_bic_technique_model <- function(df_max_user, path){
  df_max_user$bic <- 0
  df_max_user$N = 720
  df_max_user$bic <- -2 * df_max_user$log_likelyhood + df_max_user$n_params * log(df_max_user$N)  #* df_max_user$N
  df_max_user$bic <- - df_max_user$bic
  color_mapping = c("RW_without" = "dodgerblue3", "RW" = "dodgerblue", "CK_without" = "tomato3", "CK"= "tomato", "RW_CK_without" = "darkorchid3", "RW_CK" = "orchid", "trans"= "magenta4", "TRANS_D" = "chartreuse4", "TRANS_DK0"= "chartreuse", "TRANS_DCK"= "green4", "TRANS_DCK0"= "black")
  g <- ggplot() 
  g <- g + geom_bar(data = df_max_user, aes(y = bic, x = participant, group = model_name, fill=model_name), stat="identity", position = "dodge")
  g <- g + facet_grid(technique_name ~ .)
  g <- g + ggtitle( "BIC per model, technique and user" ) + xlab("User") + ylab("- Log L") + scale_fill_manual("legend", values = color_mapping )
  plot(g)
  filename <- paste(path, "bic_model_technique_users.pdf", sep="")
  ggsave( filename )
}


###########################################################################
###########################################################################
bar_plot_likelyhood_technique_model <- function(df_max_user, path){
  fill_mapping = c("RW_without" = "dodgerblue3", "RW" = "dodgerblue", "CK_without" = "tomato3", "CK"= "tomato", "RW_CK_without" = "darkorchid3", "RW_CK" = "orchid", "trans"= "magenta4", "TRANS_D" = "chartreuse4", "TRANS_DK0"= "chartreuse", "TRANS_DCK"= "green4" , "TRANS_DCK0"= "black")
  color_mapping = c("RW_without" = "none", "RW" = "black", "CK_without" = "none", "CK"= "black", "RW_CK_without" = "none", "RW_CK" = "black", "trans"= "none", "TRANS_D" = "none", "TRANS_DK0"= "black", "TRANS_DCK"= "green4" , "TRANS_DCK0"= "black")
  
  g <- ggplot() 
  g <- g + geom_bar(data = df_max_user, aes(y = log_likelyhood, x = participant, group = as.factor( model_name ), fill=model_name), stat="identity", position = "dodge")
  g <- g + facet_grid(technique_name ~ .)+ ggtitle( "Likelyhood per model, technique and user" ) + xlab("User") + ylab("-Log L") 
  g <- g + scale_fill_manual("legend", values = fill_mapping ) + scale_colour_manual("legend", values = color_mapping)
  plot(g)
  filename <- paste(path, "likelyhood_model_technique_users_1.pdf", sep="")
  ggsave( filename )
}

####################################
analyze_trans_parameter <- function ( model_name, path, graph_path ){
  
  
  v_default = -0.2
  
  if ( model_name == "trans") {
    file_vec <- list.files(path, full.names = TRUE, pattern = "log_trans")
    print( file_vec )
    datalist = lapply(file_vec, function(x){
      fl = read.csv(file=x,header=TRUE,sep=";")
      return(fl)})
    df <-  Reduce(function(x,y) {merge(x,y, all=TRUE)}, datalist)
    df['technique_name'] <- 'Traditional'
    df['temp'] = df[ 'target' ] %% 3
    df[ df['temp'] == 1, 'technique_name'] <- 'Audio'
    df[ df['temp'] == 2, 'technique_name'] <- 'Disable'
    
    df[ "HORIZON" ] <- floor( df["HORIZON"] )
    df[ df['HORIZON'] == 0 , 'B' ] <- v_default
    df[ df['HORIZON'] == 0 , 'KM' ] <- v_default
    df[ df['HORIZON'] == 0 , 'KL' ] <- v_default
    df[ df['HORIZON'] <= 1 , 'DISCOUNT' ] <- v_default

    g_horizon <- ggplot(df, aes(x=HORIZON)) + geom_histogram(binwidth = 1, colour="black", fill="white")
    g_horizon <- g_horizon+ facet_grid( rows = vars(technique_name) )
    g_horizon <- g_horizon + ylab("nb users")
  
    g_km <- ggplot(df, aes(x=KM)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_km <- g_km+ facet_grid( rows = vars(technique_name) )
    g_km <- g_km + ylab("nb users")
  
    g_kl <- ggplot(df, aes(x=KL)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_kl <- g_kl+ facet_grid( rows = vars(technique_name) )
    g_kl <- g_kl  + ylab("nb users")
  
    g_discount <- ggplot(df, aes(x=DISCOUNT)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_discount <- g_discount+ facet_grid( rows = vars(technique_name) )
    g_discount <- g_discount  + ylab("nb users")
  
    g_B <- ggplot(df, aes(x=B)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_B <- g_B+ facet_grid( rows = vars(technique_name) )
    g_B <- g_B  + ylab("nb users")
  

    p <- plot_grid(g_km, g_kl, g_horizon, g_discount, g_B, ncol=5, labels = c(" Alpha Menu", "Alpha Learning", "  Horizon", "  Discount", "     Beta" ) )
    plot(p)
    filename <- paste(graph_path, model_name, sep="/")
    filename <- paste(filename, "_params.pdf", sep="")
    ggsave( filename )
  }
  
  if ( model_name == "TRANS_D") {
    file_vec <- list.files(path, full.names = TRUE, pattern = "log_TRANS_D")
    print( file_vec )
    datalist = lapply(file_vec, function(x){
      fl = read.csv(file=x,header=TRUE,sep=";")
      return(fl)})
    df <-  Reduce(function(x,y) {merge(x,y, all=TRUE)}, datalist)
    df['technique_name'] <- 'Traditional'
    df['temp'] = df[ 'target' ] %% 3
    df[ df['temp'] == 1, 'technique_name'] <- 'Audio'
    df[ df['temp'] == 2, 'technique_name'] <- 'Disable'
    
    df[ "HORIZON" ] <- floor( df["HORIZON"] )
    df[ df['HORIZON'] == 0 , 'B' ] <- v_default
    df[ df['HORIZON'] == 0 , 'KM' ] <- v_default
    df[ df['HORIZON'] == 0 , 'KL' ] <- v_default
    df[ df['HORIZON'] == 0 , 'DECAY' ] <- v_default / 100
    
    View(df)  
    g_horizon <- ggplot(df, aes(x=HORIZON)) + geom_histogram(binwidth = 1, colour="black", fill="white")
    g_horizon <- g_horizon+ facet_grid( rows = vars(technique_name) )
    g_horizon <- g_horizon + ylab("nb users")
    
    g_km <- ggplot(df, aes(x=KM)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_km <- g_km+ facet_grid( rows = vars(technique_name) )
    g_km <- g_km + ylab("nb users")
    
    g_kl <- ggplot(df, aes(x=KL)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_kl <- g_kl+ facet_grid( rows = vars(technique_name) )
    g_kl <- g_kl  + ylab("nb users")
    
    g_decay <- ggplot(df, aes(x=DECAY)) + geom_histogram(binwidth = 0.001, colour="black", fill="white")
    g_decay <- g_decay + facet_grid( rows = vars(technique_name) )
    g_decay <- g_decay  + ylab("nb users")
    
    g_B <- ggplot(df, aes(x=B)) + geom_histogram(binwidth = 0.01, colour="black", fill="white")
    g_B <- g_B+ facet_grid( rows = vars(technique_name) )
    g_B <- g_B  + ylab("nb users")
    
    
    p <- plot_grid(g_km, g_kl, g_horizon, g_decay, g_B, ncol=5, labels = c(" Alpha Menu", "Alpha Learning", "  Horizon", "  Decay", "     Beta" ) )
    plot(p)
    filename <- paste(graph_path, model_name, sep="/")
    filename <- paste(filename, "_params.pdf", sep="")
    ggsave( filename )
    
    #g_coord <- ggparcoord(df, columns=6:10, groupColumn=11, alphaLines = 0.3, scale="globalminmax")
    
#    cr <- mutate(df, KM, KL, DECAY, technique_name)
#    g_coord <- ggparcoord(df, columns=6:10, groupColumn=11, alphaLines = 0.3, scale="globalminmax")
    g_coord <- ggparcoord(df, columns= c(6,7,10), groupColumn=11, alphaLines = 0.3, scale="uniminmax")
    #scale = globalminmax uniminmax
    plot(g_coord)
  }
  
  if (model_name == "RW_CK"){
    file_vec <- list.files(path, full.names = TRUE, pattern = "log_RW_CK")
    print( file_vec )
    datalist = lapply(file_vec, function(x){
      fl = read.csv(file=x,header=TRUE,sep=";")
      return(fl)})
    df <-  Reduce(function(x,y) {merge(x,y, all=TRUE)}, datalist)
    df['technique_name'] <- 'Traditional'
    df['temp'] = df[ 'target' ] %% 3
    df[ df['temp'] == 1, 'technique_name'] <- 'Audio'
    df[ df['temp'] == 2, 'technique_name'] <- 'Disable'
    View(df)   
    g_A_RW <- ggplot(df, aes(x=ALPHA_RW)) + geom_histogram(binwidth = 0.05, colour="black", fill="white")
    g_A_RW <- g_A_RW + facet_grid( rows = vars(technique_name) )
    g_A_RW <- g_A_RW + ylab("nb users")
    
    g_B_RW <- ggplot(df, aes(x=BETA_RW)) + geom_histogram(binwidth = 0.05, colour="black", fill="white")
    g_B_RW <- g_B_RW + facet_grid( rows = vars(technique_name) )
    g_B_RW <- g_B_RW + ylab("nb users")
    
    g_V0_RW <- ggplot(df, aes(x=V0_RW)) + geom_histogram(binwidth = 0.05, colour="black", fill="white")
    g_V0_RW <- g_V0_RW + facet_grid( rows = vars(technique_name) )
    g_V0_RW <- g_V0_RW + ylab("nb users")
    
    g_A_CK <- ggplot(df, aes(x=ALPHA_CK)) + geom_histogram(binwidth = 0.05, colour="black", fill="white")
    g_A_CK <- g_A_RW + facet_grid( rows = vars(technique_name) )
    g_A_CK <- g_A_CK + ylab("nb users")
    
    g_B_CK <- ggplot(df, aes(x=BETA_CK)) + geom_histogram(binwidth = 0.05, colour="black", fill="white")
    g_B_CK <- g_B_CK + facet_grid( rows = vars(technique_name) )
    g_B_CK <- g_B_CK + ylab("nb users")
    
    g_V0_CK <- ggplot(df, aes(x=V0_CK)) + geom_histogram(binwidth = 0.05, colour="black", fill="white")
    g_V0_CK <- g_V0_CK + facet_grid( rows = vars(technique_name) )
    g_V0_CK <- g_V0_CK + ylab("nb users")
    
    
    
    p <- plot_grid(g_A_RW, g_B_RW, g_V0_RW, g_A_CK, g_B_CK, g_V0_CK, ncol=6, labels = c(" Alpha RW", "Beta RW", " V0 RW", " Alpha CK", " Beta CK", "V0 CK" ) )
    plot(p)
    filename <- paste(graph_path, model_name, sep="/")
    filename <- paste(filename, "_params.pdf", sep="")
    ggsave( filename )
  }
  
}



##############################
parallel_coord <- function(df_original, nb_param, graph_path) {
  
}



####################################
load_data_frame <-function(path){
  file_vec <- list.files(path, full.names = TRUE, pattern = "log_")
  print( file_vec )
  datalist = lapply(file_vec, function(x){
    fl = read.csv(file=x,header=TRUE,sep=";")
    my_vars <- c("model_name", "target", "log_likelyhood", "n_params" )
    fl <- fl[ my_vars ]
    return(fl)})
  res <-  Reduce(function(x,y) {merge(x,y, all=TRUE)}, datalist)
  res['technique_name'] <- 'Traditional'
  res['temp'] = res[ 'target' ] %% 3
  res[ res['temp'] == 1, 'technique_name'] <- 'Audio'
  res[ res['temp'] == 2, 'technique_name'] <- 'Disable'
  res['participant'] = floor( res["target"] / 3 )
  
  
  
  return( res )
}


###################################
main <- function(){
  db_path <- "/Users/bailly/GARDEN/transition_model/likelyhood/optimisation"
  graph_path <- "/Users/bailly/GARDEN/transition_model/graphs/fitting_optimisation/"
  
  #analyze_trans_parameter( "TRANS_D", db_path, graph_path )
  #analyze_trans_parameter( "RW_CK", db_path, graph_path )
  
  df <- load_data_frame(db_path)
  level_order <- c("RW_without", "CK_without", "RW_CK_without", "trans", "TRANS_D",  "TRANS_DCK", "RW",  "CK",  "RW_CK",  "TRANS_DK0", "TRANS_DCK0")
  df$model_name <-factor(df$model_name, level_order)
  df <- df %>% filter(model_name != "trans")
  df<- df %>% group_by(model_name, target) %>%  filter(log_likelyhood != -1000)
  df<- df %>%group_by(model_name, target) %>%  filter(log_likelyhood == min(log_likelyhood))
  View(df)  
  bar_plot_likelyhood_technique_model(df,graph_path)
  bar_plot_bic_technique_model(df, graph_path)
  
  
  
  
  
  
  
  
  #df <- df %>%filter(model_name!="IG" & model_name != "random") %>% arrange(user_id, p1, p2, model_name)
  #df <- df %>%filter(model_name=="RW_CK" | model_name == "CK") %>% arrange(user_id, p1, p2, model_name)
  #df <- df %>%filter(log_likelyhood >-5000)
  
  #View(df)
  #bar_plot_bic_model(df, graph_path)
  #bar_plot_bic_model_technique(df, graph_path)
  #all_likelyhood_per_param_model(df, graph_path)
  #best_params_techniques(df, graph_path)

  #scatter_plot_likelyhood_hotkeycount_technique_model(df, graph_path)
  #parallel_coord(df, 4, graph_path)
  #the_best_params <- best_params_users(df, graph_path)
  #View(the_best_params)
  #distrib_params(the_best_params, graph_path)
  
  
  
  #analyze_one_param_model(df, "random", "b", graph_path)
  #analyze_one_param_model(df, "win_stay_loose_shift", "eps", graph_path)
  #analyze_two_param_model(df, "rescorla_wagner", c("alpha", "beta"), graph_path)
  #analyze_two_param_model(df, "choice_kernel", c("alpha_c", "beta_c"), graph_path)
  #analyze_more_param_model(df, "rescorla_wagner_choice_kernel", c("alpha_c", "beta_c"), graph_path)
  
  return(df)
}



####################################
load_confusion_matrix <-function(path){
  df = read.csv(file=path,header=TRUE,sep=";")
  level_order <- c("Menu", "Hotkey", "Learning")
  df$user_strategy <- factor(df$user_strategy, c("Learning", "Hotkey", "Menu"))
  df$pred_strategy <- factor(df$pred_strategy, c("Menu", "Hotkey", "Learning"))
  return (df)
}

###################################
study_confusion_matrix <- function(path, graph_path, user, type){
  df = load_confusion_matrix(path)
  
  df$value = 0
  if ( type == "n" ){
    df$value = df$n
  }else if( type == "percent" ){
    df <- df %>% filter(df$total_user != 0)
    df$value = df$n * 100 / df$total_user
  }else if( type == "likelyhood" ){
    df <- df %>% filter(df$total_user != 0)
    df$value = df$likelyhood * 100.
  }
  
  if(user == TRUE){
    df <- df %>% group_by(model, user, user_strategy, pred_strategy) %>% summarize(value = mean( value ))
  }else{
    df <- df %>% group_by(model, user_strategy, pred_strategy) %>% summarize( value = mean( value ) )
  }

  g <- plot_confusion_matrix(df)
  save_plot_confusion_matrix( graph_path, g, user, type)
  
}



####################################
plot_confusion_matrix <-function(df){
  View(df)
  g <- ggplot( data = df, aes(pred_strategy, user_strategy) ) 
  g <- g + geom_tile( aes(fill=value), colour = "white" )
  g <- g + geom_text(aes(label = sprintf("%1.0f", value)), vjust = 1) 
  g <- g + scale_fill_gradient(low = "white", high = "steelblue" )
  if ("user" %in% colnames(df) ){
    g <- g + facet_wrap(model~user, ncol= length( unique(df$user)) )
  }else{
    g <- g + facet_wrap(~model)
  }
  plot(g)
  return(g)
}

####################################
save_plot_confusion_matrix <-function(graph_path, g, user, type){
  s = "_"
  if (user == TRUE){
    s = "user_"
  }
  filename <- paste(graph_path, toString(user), sep="")
  filename <- paste(filename, type, sep="_")
  filename <- paste(filename, ".pdf", sep="")
  ggsave( filename ) 
}



#######################################
#          Main                       #
#######################################
df = main()
#path = "/Users/bailly/GARDEN/transition_model/meta_analysis/model_fit_confusion_matrix.csv"
#graph_path = "/Users/bailly/GARDEN/transition_model/graphs/confusion_matrix/confusion_matrix"

#df = study_confusion_matrix(path, graph_path, TRUE, "likelyhood")
#df = study_confusion_matrix(path, graph_path, FALSE, "likelyhood")



