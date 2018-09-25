echo off
cls

rem *********************************************
rem ************* INPUT ARGUMENTS ***************
rem *********************************************

echo *** General options ***
set /p programFolder=Program folder: 
set /p baseFolder=Working folder: 
echo :
echo *** QuiXML file options ***
set /p QuiXMLFile=QuiXMLFile (or, better, the XLS associated): 
echo :
echo *** Systems Biology options *** 
echo *** NOTE1: these files must be in the working folder
echo *** NOTE3: paste only the file name without the full path
echo *** NOTE3: please, make sure the protein identifiers used
echo ***        are the same as in the QuiXML file
echo ***        (usually, the FASTAProteinDescription)
set /p GOconnectFile=GOconnectFile (relations for categories): 
set /p GOconnectPaths=GOconnectFile (all paths): 
set /p MinimumProteins=Minimum number of proteins in category: 
set /p MaxFDR=Maximum FDR of category: 

rem *********************************************
rem ************* DEFINE VARIABLES **************
rem *********************************************

echo :
echo starting...
set ext=exe

rem location of main folders
set dataSubFolder=data
set moreData=additional_data
set statsData=stats
set outliersData=using_outliers
set graphsData=graphs
set dataFolder=%baseFolder%\%dataSubFolder%
set extraDataFolder=%baseFolder%\%moreData%
set graphFolder=%baseFolder%\%graphsData%
set outliersGraphFolder=%graphFolder%\%outliersData%
set statsFolder=%dataFolder%\%statsData%

rem creation of main folders if needed
if not exist %dataFolder% mkdir %dataFolder%
if not exist %extraDataFolder% mkdir %extraDataFolder%
if not exist %graphFolder% mkdir %graphFolder%
if not exist %outliersGraphFolder% mkdir %outliersGraphFolder%
if not exist %statsFolder% mkdir %statsFolder%

rem location of programs
set xml2tsv=%programFolder%\xml2tsv.%ext%
set klibrate=%programFolder%\klibrate.%ext%
set sanxot=%programFolder%\sanxot.%ext%
set sanxotsieve=%programFolder%\sanxotsieve.%ext%
set sanxotsqueezer=%programFolder%\sanxotsqueezer.%ext%
set sanxotgauss=%programFolder%\sanxotgauss.%ext%
set sanson=%programFolder%\sanson.%ext%
set arbor=%programFolder%\arbor.%ext%
set aljamia=%programFolder%\aljamia.%ext%

rem main features of filenames
set scanLevel=scan
set peptideLevel=peptide
set proteinLevel=protein
set categoryLevel=category
set categoryToGrandMeanLevel=categoryGrandMean
set proteinToGrandMeanLevel=proteinGrandMean
set spIntegration=scan2peptide
set pqIntegration=peptide2protein
set qcIntegration=protein2category
set spRels=scan2peptide_relations
set pqRels=peptide2proteins_relations
set XsColumn=Xs
set VsColumn=Vs

rem input files
set QuiXMLFileFullPath=%baseFolder%\%QuiXMLFile%
set GOconnectFileFullPath=%baseFolder%\%GOconnectFile%
set GOconnectPathsFullPath=%baseFolder%\%GOconnectPaths%
set GOconnectFileCleanedFullPath=%extraDataFolder%\%GOconnectFile%_cleaned.xls

rem main data files
set scanFile=%dataFolder%\%scanLevel%.xls
set peptideFile=%dataFolder%\%peptideLevel%.xls
set proteinFile=%dataFolder%\%proteinLevel%.xls
set categoryFile=%dataFolder%\%categoryLevel%.xls
set graphDataFile=%extraDataFolder%\calibrationDataFile.xls

rem files for graphs of sigmoids and calibration
set graphVValueFile=%graphFolder%\calibrationWeights.png
set graphVRankFile=%graphFolder%\calibrationRanks.png
set scan2peptideSigmoidFile=%graphFolder%\%spIntegration%.png
set peptide2proteinSigmoidFile=%graphFolder%\%pqIntegration%.png
set protein2allSigmoidFile=%graphFolder%\%proteinToGrandMeanLevel%.png
set protein2categorySigmoidFile=%graphFolder%\%qcIntegration%.png
set category2allSigmoidFile=%graphFolder%\%categoryToGrandMeanLevel%.png

rem files for graphs of sigmoids including outliers
rem not used: set protein2allSigmoidOutliersFile=%baseFolder%\%proteinToGrandMeanLevel%_outliers.png
set scan2peptideSigmoidOutliersFile=%graphFolder%\%spIntegration%_outliers.png
set peptide2proteinSigmoidOutliersFile=%graphFolder%\%pqIntegration%_outliers.png
set protein2categorySigmoidOutliersFile=%graphFolder%\%qcIntegration%_outliers.png
set protein2categoryStatsFile_iOutliers=%outliersGraphFolder%\%qcIntegration%_iOuts_stats.xls
set category2allStatsFile_iOutliers=%outliersGraphFolder%\%categoryToGrandMeanLevel%_iOuts_stats.xls

rem stats files
set scan2peptideStatsFile=%statsFolder%\%spIntegration%_stats.xls
set peptide2proteinStatsFile=%statsFolder%\%pqIntegration%_stats.xls
set protein2allStatsFile=%statsFolder%\%proteinToGrandMeanLevel%_stats.xls
set protein2categoryStatsFile=%statsFolder%\%qcIntegration%_stats.xls
set category2allStatsFile=%statsFolder%\%categoryToGrandMeanLevel%_stats.xls

rem systems biology files
set categoryListFile=%dataFolder%\selected_categories.txt
set sansonClustersFile=%dataFolder%\category_clusters.xls

rem systems biology graphs
set arborGraphFile=%graphFolder%\arbor_graph.png
set sansonGraphFile=%graphFolder%\similarity_graph.png
set gaussGraphFile=%graphFolder%\category_sigmoids.png

rem systems biology graphs, including outliers
set categoryListOutliersFile=%outliersGraphFolder%\category_selection_outliers.txt
set sansonClustersOutliersFile=%outliersGraphFolder%\category_clusters_outliers.xls
set category2allSigmoidOutliersFile=%outliersGraphFolder%\%categoryToGrandMeanLevel%_outliers.png
set arborOutliersGraphFile=%outliersGraphFolder%\arbor_graph_outliers.png
set sansonOutliersGraphFile=%outliersGraphFolder%\similarity_graph_outliers.png
set gaussOutliersGraphFile=%outliersGraphFolder%\category_sigmoids_outliers.png

if exist %programFolder% cd %programFolder%

rem *********************************************
rem ********* PART 0: creation of files *********
rem *********************************************

rem extract scan data file
%aljamia% -x%QuiXMLFileFullPath% -p%extraDataFolder% -a%scanLevel% -o%scanLevel%_uncalibrated.xls -f"[st_excluded]!=excluded" -i"[RAWFileName]-[FirstScan]-[Charge]" -j"[%XsColumn%]" -k"[%VsColumn%]" -R24

rem extract relations files
%aljamia% -x%QuiXMLFileFullPath% -p%extraDataFolder% -a%spRels% -o%spRels%.xls -i"[Sequence]" -j"[RAWFileName]-[FirstScan]-[Charge]" -R24
%aljamia% -x%QuiXMLFileFullPath% -p%extraDataFolder% -a%pqRels% -o%pqRels%.xls -i"[FASTAProteinDescription]" -j"[Sequence]" -R24

rem *********************************************
rem *********** PART 1: integrations ************
rem ************ up to protein level ************
rem *********************************************

rem ********* calibration (k calculation)
%klibrate% -d%scanLevel%_uncalibrated.xls -p%extraDataFolder% -r%spRels%.xls -a%scanLevel%Cal -o%scanFile% -G%graphVValueFile% -R%graphVRankFile% -D%graphDataFile% -g

rem ********* scan to pep
rem get original variance (prior to outlier removal)
%sanxot% -d%scanFile% -p%extraDataFolder% -r%spRels%.xls -a%spIntegration%_temp -G%scan2peptideSigmoidOutliersFile% -g
rem remove outliers
%sanxotsieve% -d%scanFile% -p%extraDataFolder% -r%spRels%.xls -V%spIntegration%_temp_infoFile.txt -a%spRels%
rem reintegrate, using old variance
%sanxot% -d%scanFile% -p%extraDataFolder% -r%spRels%_cleaned.xls -a%spIntegration% -o%peptideFile% -V%spIntegration%_temp_infoFile.txt -G%scan2peptideSigmoidFile% -z%scan2peptideStatsFile% -fg

rem ********* pep to prot
rem get original variance (prior to outlier removal)
%sanxot% -d%peptideFile% -p%extraDataFolder% -r%pqRels%.xls -a%pqIntegration%_temp -G%peptide2proteinSigmoidOutliersFile% -g
rem remove outliers
%sanxotsieve% -d%peptideFile% -p%extraDataFolder% -r%pqRels%.xls -V%pqIntegration%_temp_infoFile.txt -a%pqRels%
rem reintegrate, using old variance
%sanxot% -d%peptideFile% -p%extraDataFolder% -r%pqRels%_cleaned.xls -a%pqIntegration% -o%proteinFile% -V%pqIntegration%_temp_infoFile.txt -G%peptide2proteinSigmoidFile% -z%peptide2proteinStatsFile% -fg

rem *********************************************
rem ****** PART 2: systems biology triangle *****
rem ************* (removing outliers) ***********
rem *********************************************

rem ********* SB triangle
rem ********* q to GO
rem get original variance (prior to outlier removal)
%sanxot% -d%proteinFile% -r%GOconnectFileFullPath% -p%extraDataFolder% -a%qcIntegration%_temp_varN -G%protein2categorySigmoidOutliersFile% -z%protein2categoryStatsFile_iOutliers% -g
rem remove outliers
%sanxotsieve% -d%proteinFile% -r%GOconnectFileFullPath% -p%extraDataFolder% -V%qcIntegration%_temp_varN_infoFile.txt -a%qcIntegration%_varN -n%GOconnectFileCleanedFullPath%
rem reintegrate, using old variance
%sanxot% -d%proteinFile% -r%GOconnectFileCleanedFullPath% -p%extraDataFolder% -a%qcIntegration%_varN -o%categoryFile% -V%qcIntegration%_temp_varN_infoFile.txt -G%protein2categorySigmoidFile% -z%protein2categoryStatsFile% -fg

rem ********* GO to all
%sanxot% -d%categoryFile% -p%extraDataFolder% -a%categoryToGrandMeanLevel%_varN -o%categoryToGrandMeanLevel%.xls -Cg -v1
%sanxot% -d%categoryFile% -p%extraDataFolder% -a%categoryToGrandMeanLevel%_var0 -o%categoryToGrandMeanLevel%_var0.xls -v0 -G%category2allSigmoidFile% -z%category2allStatsFile% -Cfg

rem ********* q to all
%sanxot% -d%proteinFile% -p%extraDataFolder% -a%proteinToGrandMeanLevel% -o%proteinToGrandMeanLevel%.xls -V%qcIntegration%_temp_varN_infoFile.txt -G%protein2allSigmoidFile% -z%protein2allStatsFile% -Cfg

rem *********************************************
rem ********* PART 2b: creation of graphs *******
rem ************* (removing outliers) ***********
rem *********************************************

rem ********* SanXoTSqueezer creates the list of changing categories
%sanxotsqueezer% -l%protein2categoryStatsFile% -u%category2allStatsFile% -n%MinimumProteins% -f%MaxFDR% -p%extraDataFolder% -a%categoryLevel%Squeezed -o%categoryListFile%

rem ********* SanXoTGauss creates the graph of coloured sigmoids
%sanxotgauss% -p%extraDataFolder% -a%categoryLevel%Gaussians -z%protein2allStatsFile% -r%GOconnectFileCleanedFullPath% -c%categoryListFile% -d1000 -G%gaussGraphFile% -s5 -g

rem ********* Sanson creates the similarity graphs with clusters
%sanson% -p%extraDataFolder% -a%categoryLevel%Similarities -z%protein2allStatsFile% -r%GOconnectFileCleanedFullPath% -c%categoryListFile% -G%sansonGraphFile%

rem ********* Arbor creates the tree graph
%arbor% -p%extraDataFolder% -a%categoryLevel%Arbor -z%protein2allStatsFile% -r%GOconnectFileCleanedFullPath% -c%categoryListFile% -b%GOconnectPathsFullPath% -G%arborGraphFile%

rem *********************************************
rem ****** PART 3: systems biology triangle *****
rem ************* (INCLUDING outliers) **********
rem *********************************************

rem ********* GO to all
%sanxot% -d%qcIntegration%_temp_varN_higherLevel.xls -p%extraDataFolder% -a%categoryToGrandMeanLevel%_iOuts_varN -o%categoryToGrandMeanLevel%_iOuts.xls -Cg -v1
%sanxot% -d%qcIntegration%_temp_varN_higherLevel.xls -p%extraDataFolder% -a%categoryToGrandMeanLevel%_iOuts_var0 -o%categoryToGrandMeanLevel%_iOuts_var0.xls -v0 -G%category2allSigmoidOutliersFile% -z%category2allStatsFile_iOutliers% -Cfg


rem *********************************************
rem ********* PART 3b: creation of graphs *******
rem ************* (INCLUDING outliers) **********
rem *********************************************

rem ********* SanXoTSqueezer creates the list of changing categories
%sanxotsqueezer% -l%protein2categoryStatsFile_iOutliers% -u%category2allStatsFile_iOutliers% -n%MinimumProteins% -f%MaxFDR% -p%extraDataFolder% -a%categoryLevel%Squeezed_iOuts -o%categoryListOutliersFile%

rem ********* SanXoTGauss creates the graph of coloured sigmoids
%sanxotgauss% -p%extraDataFolder% -a%categoryLevel%Gaussians_iOuts -z%protein2allStatsFile% -r%GOconnectFileFullPath% -c%categoryListOutliersFile% -d1000 -G%gaussOutliersGraphFile% -s5 -g

rem ********* Sanson creates the similarity graphs with clusters
%sanson% -p%extraDataFolder% -a%categoryLevel%Similarities_iOuts -z%protein2allStatsFile% -r%GOconnectFileFullPath% -c%categoryListOutliersFile% -G%sansonOutliersGraphFile%

rem ********* Arbor creates the tree graph
%arbor% -p%extraDataFolder% -a%categoryLevel%Arbor_iOuts -z%protein2allStatsFile% -r%GOconnectFileFullPath% -c%categoryListOutliersFile% -b%GOconnectPathsFullPath% -G%arborOutliersGraphFile%

echo on