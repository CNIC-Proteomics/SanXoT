(WD <- getwd())
if (!is.null(WD)) setwd(WD)

source(paste0(WD,"/Config.txt"))

if (TagsUsed=="ALL"){
  
  if (Typeoflabel == "TMT"){
    
    TagsUsed<-c("126","127_N","127_C","128_N","128_C","129_N","129_C","130_N","130_C","131")
    
  } else {
    
    TagsUsed<-c("113","114","115","116","117","118","119","121")}}

for (i in TagsUsed) {
    
    for (j in Expto){
        
        if ((file.exists(paste(WD,"/",j,"/SanXoT/",i,"/data/Q2A_outStats.xls",sep=""))) == TRUE){
            
            read=read.table(paste(WD,"/",j,"/SanXoT/",i,"/data/Q2A_outStats.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
            
            read=cbind(read,Tag=i)
            
            read=cbind(read,Expto=j)
            
            directory=paste0(WD,"/",j,"/Absolute_Quantification")
            
            setwd(directory)
            
            write.csv(read, file=paste(j,i,"Q2A_outStats.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="Q2A_outStats.xls")

All <- do.call(rbind,lapply(files, read.csv, row.names=NULL))

All<-unique(All)

write.csv(All, "All_experiment_Q2A_outStats.csv")

file.remove(files)

for (i in TagsUsed) {
    
    for (j in Expto){
        
        if ((file.exists(paste(WD,"/",j,"/SanXoT/",i,"/data/protein_ABS.xls",sep=""))) == TRUE){
            
            read=read.table(paste(WD,"/",j,"/SanXoT/",i,"/data/protein_ABS.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
            
            read=cbind(read,Tag=i)
            
            read=cbind(read,Expto=j)
            
            directory=paste0(WD,"/",j,"/Absolute_Quantification")
            
            setwd(directory)
            
            write.csv(read, file=paste(j,i,"protein_ABS.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="protein_ABS.xls")

All <- do.call(rbind,lapply(files, read.csv, row.names=NULL))

All<-unique(All)

write.csv(All, "All_experiment_protein_ABS.csv")

file.remove(files)

for (i in TagsUsed) {
    
    for (j in Expto){
        
        if ((file.exists(paste(WD,"/",j,"/SanXoT/",i,"/data/All_ABS.xls",sep=""))) == TRUE){
            
            read=read.table(paste(WD,"/",j,"/SanXoT/",i,"/data/All_ABS.xls",sep=""), sep="\t", comment.char = "¡",quote = "¿", header=TRUE)
            
            read=cbind(read,Tag=i)
            
            read=cbind(read,Expto=j)
            
            directory=paste0(WD,"/",j,"/Absolute_Quantification")
            
            setwd(directory)
            
            write.csv(read, file=paste(j,i,"All_ABS.xls", sep="_"), sep="\t", row.names=FALSE)}}}

files <- list.files(path = directory,pattern="All_ABS.xls")

All <- do.call(rbind,lapply(files, read.csv, row.names=NULL))

All<-unique(All)

write.csv(All, "All_experiment_All_ABS.csv")

file.remove(files)

Q2A_outStats<-read.csv("All_experiment_Q2A_outStats.csv",header=TRUE)
Q2A_outStats<-cbind(Q2A_outStats,Protein_tag_Expto=paste(Q2A_outStats$idinf,Q2A_outStats$Tag,Q2A_outStats$Expto,sep="_"))

protein_ABS<-read.csv("All_experiment_protein_ABS.csv",header=TRUE)
protein_ABS<-cbind(protein_ABS,Protein_tag_Expto=paste(protein_ABS$idsup,protein_ABS$Tag,protein_ABS$Expto,sep="_"))
protein_ABS<-protein_ABS[c(7,4)]
protein_ABS<-unique(protein_ABS)
colnames(protein_ABS)=c("Protein_tag_Expto","SumI")

All_data<-merge(Q2A_outStats,protein_ABS,all.y=TRUE)
All_data<-All_data[c(4,5,6,7,8,9,10,11,13,14,15)]
All_data<-cbind(All_data,Tag_Expto=paste(All_data$Tag,All_data$Expto,sep="_"))

All_ABS<-read.csv("All_experiment_All_ABS.csv",header=TRUE)
All_ABS<-cbind(All_ABS,Tag_Expto=paste(All_ABS$Tag,All_ABS$Expto,sep="_"))
All_ABS<-All_ABS[c(7,4)]
colnames(All_ABS)=c("Tag_Expto","SUMSumI")
All_data<-merge(All_data,All_ABS,all=TRUE)

write.csv(All_data, "All_data_experiment_All_ABS.csv")