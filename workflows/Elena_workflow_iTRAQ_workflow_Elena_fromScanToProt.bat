echo off
cls

rem *********************************************
rem ************* INPUT ARGUMENTS ***************
rem *********************************************

echo *** General options ***
set /p programFolder=Program folder: 
set /p drive=Drive for program folder (C:, S:, etc): 
set /p baseFolder=Working folder: 
echo :
echo *** QuiXML file options ***
set /p QuiXMLFile=QuiXMLFile (or, better, the XLS associated): 
set /p FirstIon=First reporter ion: 
set /p SecondIon=Second reporter ion: 
echo :

%drive%
cd %programFolder%

rem *********************************************
rem ************* DEFINE VARIABLES **************
rem *********************************************

echo :
echo starting...
set ext=py

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
set spIntegration=scan2peptide
set pqIntegration=peptide2protein
set spRels=scan2peptide_relations
set pqRels=peptide2proteins_relations
set XsColumn=q_Xs_%FirstIon%_%SecondIon%
set VsColumn=q_Vs_%FirstIon%_%SecondIon%

rem input files
set QuiXMLFileFullPath=%baseFolder%\%QuiXMLFile%

rem main data files
set scanFile=%dataFolder%\%scanLevel%.xls
set peptideFile=%dataFolder%\%peptideLevel%.xls
set proteinFile=%dataFolder%\%proteinLevel%.xls
set graphDataFile=%extraDataFolder%\calibrationDataFile.xls

rem files for graphs of sigmoids and calibration
set graphVValueFile=%graphFolder%\calibrationWeights.png
set graphVRankFile=%graphFolder%\calibrationRanks.png
set scan2peptideSigmoidFile=%graphFolder%\%spIntegration%.png
set peptide2proteinSigmoidFile=%graphFolder%\%pqIntegration%.png

rem files for graphs of sigmoids including outliers
set scan2peptideSigmoidOutliersFile=%graphFolder%\%spIntegration%_outliers.png
set peptide2proteinSigmoidOutliersFile=%graphFolder%\%pqIntegration%_outliers.png

rem stats files
set scan2peptideStatsFile=%statsFolder%\%spIntegration%_stats.xls
set peptide2proteinStatsFile=%statsFolder%\%pqIntegration%_stats.xls

if exist %programFolder% cd %programFolder%

rem *********************************************
rem ********* PART 0: creation of files *********
rem *********************************************

rem extract scan data file
%aljamia% -x%QuiXMLFileFullPath% -p%extraDataFolder% -a%scanLevel% -o%scanLevel%_uncalibrated.xls -i"[RAWFileName]-[FirstScan]-[Charge]" -j"[%XsColumn%]" -k"[%VsColumn%]" -R24

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


echo on