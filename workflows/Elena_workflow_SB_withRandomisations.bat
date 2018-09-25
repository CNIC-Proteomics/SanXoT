set /p programFolder=Program folder: 
set /p drive=Drive for program folder (C:, S:, etc): 
set /p protData=Protein data (tab separated values file): 
set /p relationsData=SB elations file (protein to category): 
set /p experimentName=Experiment preffix: 
set /p workingFolder=Working folder: 
if not exist %workingFolder% mkdir %workingFolder%

%drive%
cd %programFolder%

rem ******** important, put here the experiment code containing the median *********
rem ******** no need to write numerical value, but you can do it here if you want: ********
REM set median=3
set ext=exe
set sanxot=%programFolder%\sanxot.%ext%
set sanxotSieve=%programFolder%\sanxotsieve.%ext%
set sanxotSqueezer=%programFolder%\sanxotsqueezer.%ext%
set sanson=%programFolder%\sanson.%ext%
set sanxotgauss=%programFolder%\sanxotgauss.%ext%
set anselmo=%programFolder%\anselmo.%ext%


REM ************* FIRST PART *************
REM from protein to cat calculating its own variance
%sanxot% -d%protData% -p%workingFolder% -r%relationsData% -a%experimentName%_q2c_varN_inOuts -gD

REM removing outliers from prot to cat
%sanxotSieve% -p%workingFolder% -a%experimentName%_removingOutliers_c -r%relationsData% -d%protData% -V%experimentName%_q2c_varN_inOuts_infoFile.txt -f0.01

REM reintegrating from prot to cat with no outliers
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q2c_varN_noOuts -fg -V%experimentName%_q2c_varN_inOuts_infoFile.txt -D

REM prot to all, using variance from prot to cat
%sanxot% -p%workingFolder% -d%protData% -a%experimentName%_q2a_varQC -Cfg -V%experimentName%_q2c_varN_inOuts_infoFile.txt -D

REM REM ************* END FIRST PART *************

REM REM ************* SECOND PART *************
REM protein to randomcat using its own qr variance and q' data
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts1 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts2 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts3 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts4 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts5 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts6 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts7 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts8 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOuts9 -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsA -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsB -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsC -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsD -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsE -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsF -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsG -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsH -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsI -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsJ -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsK -RgD
%sanxot% -d%protData% -p%workingFolder% -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_q'2r_varN_noOutsL -RgD

REM rem from randomcat to all -> to get %varianceRandom2All%
%sanxot% -d%experimentName%_q'2r_varN_noOuts1_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts1 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts2_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts2 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts3_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts3 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts4_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts4 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts5_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts5 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts6_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts6 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts7_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts7 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts8_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts8 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOuts9_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts9 -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsA_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsA -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsB_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsB -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsC_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsC -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsD_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsD -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsE_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsE -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsF_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsF -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsG_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsG -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsH_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsH -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsI_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsI -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsJ_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsJ -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsK_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsK -CgD
%sanxot% -d%experimentName%_q'2r_varN_noOutsL_higherLevel.xls -p%workingFolder% -a%experimentName%_r'2a_varNN_noOutsL -CgD

%anselmo% -f%experimentName%_r'2a_varNN_noOuts -p%workingFolder% -a%experimentName%_r'2a_varNN_noOuts_anselmo

REM from cat to all with no outliers, using median variance r'2a_varNN_noOuts
%sanxot% -d%experimentName%_q2c_varN_noOuts_higherLevel.xls -p%workingFolder% -a%experimentName%_c2a_varQCR'_noOuts -Cfg -Vmed_%experimentName%_r'2a_varNN_noOuts_infoFile.txt -D
%sanxot% -d%experimentName%_q2c_varN_noOuts_higherLevel.xls -p%workingFolder% -a%experimentName%_c2a_varQCR'_noOuts -Cfg -V%experimentName%_r'2a_varNN_noOuts%median%_infoFile.txt -D
%sanxotSqueezer% -p%workingFolder% -a%experimentName%_squeezer_cR'_noOuts1FDR -l%experimentName%_q2c_varN_noOuts_outStats.xls -u%experimentName%_c2a_varQCR'_noOuts_outStats.xls -f0.01 -n5
%sanxotSqueezer% -p%workingFolder% -a%experimentName%_squeezer_cR'_noOuts5FDR -l%experimentName%_q2c_varN_noOuts_outStats.xls -u%experimentName%_c2a_varQCR'_noOuts_outStats.xls -f0.05 -n5
%sanxotSqueezer% -p%workingFolder% -a%experimentName%_squeezer_cR'_noOuts10FDR -l%experimentName%_q2c_varN_noOuts_outStats.xls -u%experimentName%_c2a_varQCR'_noOuts_outStats.xls -f0.10 -n5
%sanxotSqueezer% -p%workingFolder% -a%experimentName%_squeezer_cR'_noOuts20FDR -l%experimentName%_q2c_varN_noOuts_outStats.xls -u%experimentName%_c2a_varQCR'_noOuts_outStats.xls -f0.2 -n5
%sanson% -p%workingFolder% -z%experimentName%_q2a_varQC_outStats.xls -c%experimentName%_squeezer_cR'_noOuts_outList.xls -r%relationsData% -a%experimentName%_sanson_cR'_showingOuts -l3
%sanson% -p%workingFolder% -z%experimentName%_q2a_varQC_outStats.xls -c%experimentName%_squeezer_cR'_noOuts1FDR_outList.xls -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_sanson_cR'_noOuts1FDR -l3
%sanson% -p%workingFolder% -z%experimentName%_q2a_varQC_outStats.xls -c%experimentName%_squeezer_cR'_noOuts5FDR_outList.xls -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_sanson_cR'_noOuts5FDR -l3
%sanson% -p%workingFolder% -z%experimentName%_q2a_varQC_outStats.xls -c%experimentName%_squeezer_cR'_noOuts10FDR_outList.xls -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_sanson_cR'_noOuts10FDR -l3
%sanson% -p%workingFolder% -z%experimentName%_q2a_varQC_outStats.xls -c%experimentName%_squeezer_cR'_noOuts20FDR_outList.xls -r%experimentName%_removingOutliers_c_cleaned.xls -a%experimentName%_sanson_cR'_noOuts20FDR -l3
%sanxotgauss% -p%workingFolder% -a%experimentName%_Gauss_cR'_showingOuts -z%experimentName%_q2a_varQC_outStats.xls -r%relationsData% -c%experimentName%_squeezer_cR'_noOuts_outList.xls -d1000 -G%experimentName%_Gauss_cR'_showingOuts.png -s5 -g -l6
%sanxotgauss% -p%workingFolder% -a%experimentName%_Gauss_cR'_noOuts1FDR -z%experimentName%_q2a_varQC_outStats.xls -r%experimentName%_removingOutliers_c_cleaned.xls -c%experimentName%_squeezer_cR'_noOuts1FDR_outList.xls -d1000 -G%experimentName%_Gauss_cR'_noOuts1FDR.png -s5 -g -l6
%sanxotgauss% -p%workingFolder% -a%experimentName%_Gauss_cR'_noOuts5FDR -z%experimentName%_q2a_varQC_outStats.xls -r%experimentName%_removingOutliers_c_cleaned.xls -c%experimentName%_squeezer_cR'_noOuts5FDR_outList.xls -d1000 -G%experimentName%_Gauss_cR'_noOuts5FDR.png -s5 -g -l6
%sanxotgauss% -p%workingFolder% -a%experimentName%_Gauss_cR'_noOuts10FDR -z%experimentName%_q2a_varQC_outStats.xls -r%experimentName%_removingOutliers_c_cleaned.xls -c%experimentName%_squeezer_cR'_noOuts10FDR_outList.xls -d1000 -G%experimentName%_Gauss_cR'_noOuts10FDR.png -s5 -g -l6

%sanxotgauss% -p%workingFolder% -a%experimentName%_Gauss_cR'_noOuts20FDR -z%experimentName%_q2a_varQC_outStats.xls -r%experimentName%_removingOutliers_c_cleaned.xls -c%experimentName%_squeezer_cR'_noOuts20FDR_outList.xls -d1000 -G%experimentName%_Gauss_cR'_noOuts20FDR.png -s5 -g -l6

REM ************* END THIRD PART *************