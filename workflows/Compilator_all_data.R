(WD <- getwd())
if (!is.null(WD)) setwd(WD)

source(paste0(WD,"/Config.txt"))

if (TagsUsed=="ALL"){
  
  if (Typeoflabel == "TMT"){
    
    TagsUsed<-c("126","127_N","127_C","128_N","128_C","129_N","129_C","130_N","130_C","131")
    
  } else {
    
    TagsUsed<-c("113","114","115","116","117","118","119","121")}}

for (i in tags) {
  
  for (j in Expto){
    
    if ((file.exists(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/Q2A_outStats.xls",sep=""))) == TRUE){
      
      read=read.table(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/Q2A_outStats.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
      
      read=cbind(read,Tag=i)
      
      read=cbind(read,Expto=j)
      
      directory=c(paste0(WD,"/Results_tables"))
      
      setwd(directory)
      
      write.table(read, file=paste(j,i,"Q2A_outStats.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="Q2A_outStats.xls")

All <- do.call(rbind,lapply(files, read.table, row.names=NULL, header=TRUE))

All<-unique(All)

write.table(All, "All_experiment_Q2A_outStats.xls", sep="\t", row.names=FALSE)

file.remove(files)

for (i in tags) {
  
  for (j in Expto){
    
    if ((file.exists(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/P2A_inOuts_outStats.xls",sep=""))) == TRUE){
      
      read=read.table(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/P2A_inOuts_outStats.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
      
      read=cbind(read,Tag=i)
      
      read=cbind(read,Expto=j)
      
      directory=c(paste0(WD,"/Results_tables"))
      
      setwd(directory)
      
      write.table(read, file=paste(j,i,"P2A_outStats.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="P2A_outStats.xls")

All <- do.call(rbind,lapply(files, read.table, row.names=NULL, header=TRUE))

All<-unique(All)

write.table(All, "All_experiment_P2A_outStats.xls", sep="\t", row.names=FALSE)

file.remove(files)

for (i in tags) {
  
  for (j in Expto){
    
    if ((file.exists(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/C2A_outStats.xls",sep=""))) == TRUE){
      
      read=read.table(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/C2A_outStats.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
      
      read=cbind(read,Tag=i)
      
      read=cbind(read,Expto=j)
      
      directory=c(paste0(WD,"/Results_tables"))
      
      setwd(directory)
      
      write.table(read, file=paste(j,i,"C2A_outStats.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="C2A_outStats.xls")

All <- do.call(rbind,lapply(files, read.table, row.names=NULL, header=TRUE))

All<-unique(All)

write.table(All, "All_experiment_C2A_outStats.xls", sep="\t", row.names=FALSE)

file.remove(files)

for (i in tags) {
  
  for (j in Expto){
    
    if ((file.exists(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/P2Q_inOuts_outStats.xls",sep=""))) == TRUE){
      
      read=read.table(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/P2Q_inOuts_outStats.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
      
      read=cbind(read,Tag=i)
      
      read=cbind(read,Expto=j)
      
      directory=c(paste0(WD,"/Results_tables"))
      
      setwd(directory)
      
      write.table(read, file=paste(j,i,"P2Q_inOuts_outStats.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="P2Q_inOuts_outStats.xls")

All <- do.call(rbind,lapply(files, read.table, row.names=NULL, header=TRUE))

All<-unique(All)

write.table(All, "All_experiment_P2Q_inOuts_outStats.xls", sep="\t", row.names=FALSE)

file.remove(files)

for (i in tags) {
  
  for (j in Expto){
    
    if ((file.exists(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/Q2C_inOuts_outStats.xls",sep=""))) == TRUE){
      
      read=read.table(paste(WD,"/",j,"/MSF/SanXoT/",i,"/data/Q2C_inOuts_outStats.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
      
      read=cbind(read,Tag=i)
      
      read=cbind(read,Expto=j)
      
      directory=c(paste0(WD,"/Results_tables"))
      
      setwd(directory)
      
      write.table(read, file=paste(j,i,"Q2C_inOuts_outStats.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="Q2C_inOuts_outStats.xls")

All <- do.call(rbind,lapply(files, read.table, row.names=NULL, header=TRUE))

All<-unique(All)

write.table(All, "All_experiment_Q2C_inOuts_outStats.xls", sep="\t", row.names=FALSE)

file.remove(files)

Q2C_relations<-read.table("All_experiment_Q2C_inOuts_outStats.xls",header=TRUE)
Q2C_relations<-cbind(Q2C_relations,Protein_tag_Expto=paste(Q2C_relations$idinf,Q2C_relations$Tag,Q2C_relations$Expto,sep="_"))
Q2C_relations<-cbind(Q2C_relations,Category_tag_Expto=paste(Q2C_relations$idsup,Q2C_relations$Tag,Q2C_relations$Expto,sep="_"))
Q2C_relations<-subset(Q2C_relations,select=c("Category_tag_Expto","Protein_tag_Expto","n"))
colnames(Q2C_relations)<-c("Category_tag_Expto","Protein_tag_Expto","nq")

P2Q_relations<-read.table("All_experiment_P2Q_inOuts_outStats.xls",header=TRUE)
P2Q_relations<-cbind(P2Q_relations,Sequence_tag_Expto=paste(P2Q_relations$idinf,P2Q_relations$Tag,P2Q_relations$Expto,sep="_"))
P2Q_relations<-cbind(P2Q_relations,Protein_tag_Expto=paste(P2Q_relations$idsup,P2Q_relations$Tag,P2Q_relations$Expto,sep="_"))
P2Q_relations<-subset(P2Q_relations,select=c("Protein_tag_Expto","Sequence_tag_Expto","n"))
colnames(P2Q_relations)<-c("Protein_tag_Expto","Sequence_tag_Expto","np")

Q2A_outStats<-read.table("All_experiment_Q2A_outStats.xls",header=TRUE)
Q2A_outStats<-cbind(Q2A_outStats,Protein_tag_Expto=paste(Q2A_outStats$idinf,Q2A_outStats$Tag,Q2A_outStats$Expto,sep="_"))

C2A_outStats<-read.table("All_experiment_C2A_outStats.xls",header=TRUE)
C2A_outStats<-cbind(C2A_outStats,Category_tag_Expto=paste(C2A_outStats$idinf,C2A_outStats$Tag,C2A_outStats$Expto,sep="_"))

P2A_outStats<-read.table("All_experiment_P2A_outStats.xls",header=TRUE)
P2A_outStats<-cbind(P2A_outStats,Sequence_tag_Expto=paste(P2A_outStats$idinf,P2A_outStats$Tag,P2A_outStats$Expto,sep="_"))

Q2A_data<-merge(Q2A_outStats,Q2C_relations, all=TRUE)
Q2A_data<-merge(Q2A_data,P2Q_relations, all=TRUE)

Q2A_data_def<-Q2A_data[c(1,5,9,10,12,13,14,15,16,17)]
colnames(Q2A_data_def)=c("Protein_tag_Expto","Protein","Zq","FDRq","Tag","Expto","Category_tag_Expto","nq","Sequence_tag_Expto","np")
Q2A_data_def<-merge(Q2A_data_def,P2A_outStats, all=TRUE)

Q2A_data_def<-Q2A_data_def[c(1,2,5,6,7,8,9,10,14,18,19)]
colnames(Q2A_data_def)=c("Tag","Expto","Protein","Zq","FDRq","Category_tag_Expto","nq","np","Sequence","Zp","FDRp")

Q2A_data_def<-merge(Q2A_data_def,C2A_outStats, all=TRUE)
Q2A_data_def<-Q2A_data_def[c(1,2,4,5,6,7,8,9,10,11,15,19,20)]
colnames(Q2A_data_def)=c("Tag","Expto","Protein","Zq","FDRq","nq","np","Sequence","Zp","FDRp","Category","Zc","FDRc")

write.csv(Q2A_data_def, "All_data_compiled_DB.csv")