(WD <- getwd())
if (!is.null(WD)) setwd(WD)

source(paste0(WD,"/Config.txt"))

################################################################################################################
################################################################################################################

if (TagsUsed=="ALL"){
  
  if (Typeoflabel == "TMT"){
    
    TagsUsed<-c("126","127_N","127_C","128_N","128_C","129_N","129_C","130_N","130_C","131")
    
  } else {
    
    TagsUsed<-c("113","114","115","116","117","118","119","121")}}

Tag<-c()

for (i in TagsUsed){
  for (j in Expto){
    
    tags_temp<-paste(j,i,sep="_")
    
    if (NROW(Tag)==0){
      
      Tag<-tags_temp
      
    } else {Tag<-rbind(Tag,tags_temp)}}}

Path<-c()

for (i in TagsUsed){
  for (j in Expto){
    
    path_temp<-paste(WD,"/",j,"/SanXoT/",i,"/data/Q2A_lowerNormV.xls",sep="")
    
    if (NROW(Tag)==0){
      
      Path<-path_temp
      
    } else {Path<-rbind(Path,path_temp)}}}

Tag<-as.data.frame(Tag)
row.names(Tag) <- NULL
colnames(Tag) <- "Tag"

Path<-as.data.frame(Path)
row.names(Path) <- NULL
colnames(Path) <- "Path"

Tag_file_temp<-cbind(Tag,Path)

write.table(Tag_file_temp, file=paste0(WD,"/Integration/Tag_file_temp.txt"),sep="\t", row.names = FALSE)

if (NOI == 1){
  
  Tag_file<-Tag_file_temp[Tag_file_temp$Tag %in% Integration,]
  
  write.table(Tag_file, file=paste0(WD,"/Integration/Tag_file.txt"),sep="\t", row.names = FALSE)
  
} else {
  
  for (j in Integrations) {
    
    tag<-paste(j,get(j),sep="_")
    
    for (i in tag){
      
      tag<-substring(tag,(nchar(j)+2),nchar(tag))
      
      tag<-paste(Expto,tag,sep="_")
      
      Tag_file<-Tag_file_temp[Tag_file_temp$Tag %in% tag, ]
      
      if (nrow(Tag_file)>1){
        
        write.table(Tag_file, file=paste0(WD,"/Integration/",j,"_Tag_file.txt"),sep="\t", row.names = FALSE)}}}}

