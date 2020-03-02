rm(list = ls())
library(ggplot2)
library(dplyr)
library(GGally)
library(reshape2)


###########################################################################
###########################################################################
bar_plot_likelyhood_technique_model <- function(df_original, path){
  df_max_user <- df_original %>% group_by(model_name, technique_name, user_id) %>% summarize(log_likelyhood = - max(log_likelyhood)) %>% arrange(model_name, technique_name, log_likelyhood)
  View(df_max_user)
  g <- ggplot() 
  g <- g + geom_bar(data = df_max_user, aes(y = log_likelyhood, x = user_id, group = as.factor( model_name ), fill=model_name), stat="identity", position = "dodge")
  g <- g + facet_grid(technique_name ~ .)
  g <- g + ggtitle( "Likelyhood per model, technique and user" ) + xlab("User") + ylab("-Log L")
  plot(g)
  filename <- paste(path, "likelyhood_model_technique_users_1.pdf", sep="")
  ggsave( filename )
  
  g <- ggplot() 
  g <- g + geom_bar(data = df_max_user, aes(y = log_likelyhood, x = technique_name, group = as.factor(user_id ), fill=technique_name), stat="identity", position = "dodge")
  g <- g + facet_grid(. ~ model_name)
  g <- g + ggtitle( "Likelyhood per model, technique and user" ) + xlab("User") + ylab("Log likelyhood")
  plot(g)
  filename <- paste(path, "likelyhood_model_technique_users_2.pdf", sep="")
  ggsave( filename )
  
}

#######################
bar_plot_bic_technique_model <- function(df_original, path){
  df_max_user <- df_original %>% group_by(model_name, technique_name, n_params, N, user_id) %>% summarize(log_likelyhood = max(log_likelyhood)) %>% arrange(model_name, technique_name, log_likelyhood)
  df_max_user <-df_max_user %>% filter(model_name != "random")
  df_max_user$bic <- 0
  df_max_user$bic <- -2 * df_max_user$log_likelyhood + df_max_user$n_params * log(df_max_user$N)  #* df_max_user$N
  g <- ggplot() 
  g <- g + geom_bar(data = df_max_user, aes(y = bic, x = user_id, group = as.factor(model_name ), fill=model_name), stat="identity", position = "dodge")
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




####################################
load_data_frame <-function(path){
  file_vec <- list.files(path, full.names = TRUE, pattern = "log_")
  print( file_vec )
  datalist = lapply(file_vec, function(x){
      fl = read.csv(file=x,header=TRUE,sep=";")
      return(fl)})
  res <-  Reduce(function(x,y) {merge(x,y, all=TRUE)}, datalist)
  
  res$technique_name = "Traditional"
  res$technique_name[res$technique_id == 1] <- "Audio"
  res$technique_name[res$technique_id == 2] <- "Disable"
  res$user_index = res$user_id - res$user_id%%3
  
  return( res )
}




###################################
main <- function(){
  db_path <- "/Users/bailly/GARDEN/transition_model/likelyhood/"
  graph_path <- "/Users/bailly/GARDEN/transition_model/graphs/fitting/"
  
  df <- load_data_frame(db_path)
  df <- df %>%filter(model_name!="IG" & model_name != "random") %>% arrange(user_id, p1, p2, model_name)
  #df <- df %>%filter(model_name=="RW_CK" | model_name == "CK") %>% arrange(user_id, p1, p2, model_name)
  
  #View(df)
  
  best_params_techniques(df, graph_path)
  bar_plot_likelyhood_technique_model(df,graph_path)
  bar_plot_bic_technique_model(df, graph_path)
  #scatter_plot_likelyhood_hotkeycount_technique_model(df, graph_path)
  #parallel_coord(df, 4, graph_path)
  the_best_params <- best_params_users(df, graph_path)
  View(the_best_params)
  distrib_params(the_best_params, graph_path)
  
  
  
  #analyze_one_param_model(df, "random", "b", graph_path)
  #analyze_one_param_model(df, "win_stay_loose_shift", "eps", graph_path)
  #analyze_two_param_model(df, "rescorla_wagner", c("alpha", "beta"), graph_path)
  #analyze_two_param_model(df, "choice_kernel", c("alpha_c", "beta_c"), graph_path)
  #analyze_more_param_model(df, "rescorla_wagner_choice_kernel", c("alpha_c", "beta_c"), graph_path)
  
  return(df)
}

#######################################
visualize_emmanouil_data <- function(){
  emmanouil <- read.csv(file="/Users/bailly/GARDEN/transition_model/experiment/grossman_cleaned_data.csv", header=TRUE, sep=",")
  emmanouil <- emmanouil %>% filter(user_id == 2 & ub_id == 0)
  View(emmanouil)
  #g <- ggplot() 
  #g <- g + geom_bar(data = grossman, aes(y = errors, x = user_id, fill= ub), stat= "identity")
  #g <- g + ggtitle( "error per method" ) + xlab("user id") + ylab("errors")
  #plot(g)
}

#######################################
visualize_raw_data <- function(){
  grossman <- read.csv(file="/Users/bailly/GARDEN/transition_model/experiment/other/hotkeys_formatted_dirty.csv", header=TRUE, sep=",")
  grossman <- grossman %>%filter( subject == 2 & trial_number == 260) 
  
  #grossman <- grossman %>%filter(errors == 0 & time_last_letter_press > -1 & time_menu_open > -1 ) %>% filter (time_menu_open >-1 & time_last_modifier_press > -1)
  
  
  #grossman <- grossman %>%filter( errors > 0 ) %>% filter (time_menu_open >-1 & time_last_modifier_press > -1)
  #grossman$first_selection <- substr( grossman$selection, 0, 1 )
  #grossman <- grossman %>%  filter( first_selection ==0) %>% group_by(subject, trial_number) %>% summarize( first_selection = first_selection )
  
  #emmanouil <- read.csv(file="/Users/bailly/GARDEN/transition_model/experiment/grossman_cleaned_data.csv", header=TRUE, sep=",")

  
  
  #grossman <- grossman %>% filter( technique == 2)
  
  #grossman <- grossman %>%filter(subject == 4 & trial_number == 263 )
  #grossman <- grossman %>%filter(menu_errors >0 & time_last_letter_press > 0 )
  #grossman <- grossman %>%filter(time_last_letter_press == 0  )
  #grossman <- grossman %>%filter(time_menu_open > time_last_modifier_press & time_last_letter_press != -1 & errors == 0 )
  #grossman <- grossman %>%filter(errors == 0 & time_menu_open == -1)
  #grossman <- grossman %>%filter(errors == 1 & time_last_letter_press != -1 & time_menu_open != -1)
  #grossman <- grossman %>% filter(time_last_letter_press > time_menu_open)
  #grossman <- grossman %>% filter(subject == 1) %>% filter(trial_number == 16 | trial_number == 168 | trial_number == 227 | trial_number == 364 | trial_number == 366 | trial_number == 368 | trial_number == 389 | trial_number == 422 | trial_number == 484 | trial_number == 541 | trial_number == 635 | trial_number == 639 | trial_number == 703)
  View(grossman)
  #g <- ggplot() 
  #g <- g + geom_bar(data = grossman, aes(y = errors, x = user_id, fill= ub), stat= "identity")
  #g <- g + ggtitle( "error per method" ) + xlab("user id") + ylab("errors")
  #plot(g)
}
#######################################
#          Main                       #
#######################################
#g<-ggplot()
#visualize_emmanouil_data()
#visualize_raw_data()
df = main()


