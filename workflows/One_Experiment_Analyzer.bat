@echo off

set /p BaseFolder=Base Folder (without ""):

set /p Experiments=Experiment Names (The folder/s name/s that contains the ID-q):

set /p Fractions=Fraction Names (The folder/s name/s that contains the MSFs):

set /p Tags=Tags Used in the experiment (Tags separate by "space"):

set /p ControlTag=Tag Used as control or Mean:

set /p pRatio_opt=Execute pRatio (Y/N):

set /p presanxot_opt=Execute pre-SanXoT (Y/N):

set /p tagfilemaker_opt=Execute Tag file maker (Y/N):

for %%j in (%Experiments%) do (
for %%i in (%Tags%) do (
	if not exist "%BaseFolder%\Results_tables" md "%BaseFolder%\Results_tables"
	if not exist "%BaseFolder%\%%j\SanXoT" md "%BaseFolder%\%%j\SanXoT"
	if not exist "%BaseFolder%\%%j\Pre-SanXoT" md "%BaseFolder%\%%j\Pre-SanXoT"
	if not exist "%BaseFolder%\Integration" md "%BaseFolder%\Integration"
	))

CD "C:\Users\fgarcia\Desktop\pRatio_CMD"

C:

set pRatio=pRatio.exe -t "%BaseFolder%\%%j\MSF\%%k" -d "%BaseFolder%\%%j\MSF - INV\%%k" -pd 2.x -o "%BaseFolder%\%%j\MSF\%%k_DIR" -fc .01 -dm five -dt 20 -n 229.162932 -q xcorr -fm mixed

for %%j in (%Experiments%) do (
for %%k in (%Fractions%) do (

	if %pRatio_opt% EQU y (
	start "pRatio_%%k" cmd.exe /C "(%pRatio%)"
	)))
	
	:wait_loop1
	for %%j in (%Experiments%) do (
	for %%k in (%Fractions%) do (
	if not exist "%BaseFolder%\%%j\MSF\%%k_DIR\MSF_results.xls" goto wait_loop1
	))

cd "%BaseFolder%"

S:

set Pre-SanXoT="C:\Program Files\R\R-3.2.3\bin\R.exe" -f "C:\Users\fgarcia\Desktop\Integrator\standalone exes\Pre-SanXoT.R" --slave

if %presanxot_opt% EQU y (
	start "pre-SanXoT" cmd.exe /C "(%Pre-SanXoT%)"
	)
	
set Tag_file_maker="C:\Program Files\R\R-3.2.3\bin\R.exe" -f "C:\Users\fgarcia\Desktop\Integrator\standalone exes\Tag_file_maker_V2.R" --slave

if %tagfilemaker_opt% EQU y (
	start "Tag file maker V2" cmd.exe /C "(%Tag_file_maker%)"
	)

cd "C:\Users\fgarcia\Desktop\Integrator\standalone exes"

C:

set Q2CRelationFile="S:\U_Proteomica\UNIDAD\DatosCrudos\laboratorio\SPIROS\q2cIPA-DAVID-CORUM-Manual-Human3_nd.txt"
set Data=ID-q.txt

set aljamiaSData=aljamia.exe -x"%BaseFolder%\%%j\Pre-SanXoT\%Data%" -p"%BaseFolder%\%%j\SanXoT\%%i\additional_data" -o"Scans_uncalibrated.xls" -aS2P_inOUTs_uncalibrated -i"[Raw_FirstScan]-[Charge]" -j"[Xs_%%i_%ControlTag%]" -k"[Vs_%%i_%ControlTag%]" -R1
set aljamiaS2PRels=aljamia.exe -x"%BaseFolder%\%%j\Pre-SanXoT\%Data%" -p"%BaseFolder%\%%j\SanXoT\%%i\additional_data" -o"S2P_RelationsFile.xls" -aS2P_RelationsFile -i"[Sequence]" -j"[Raw_FirstScan]-[Charge]" -R1
set aljamiaP2QRels=aljamia.exe -x"%BaseFolder%\%%j\Pre-SanXoT\%Data%" -p"%BaseFolder%\%%j\SanXoT\%%i\additional_data" -o"P2Q_RelationsFile.xls" -aP2Q_RelationsFile -i"[FASTAProteinDescription]" -j"[Sequence]" -R1

set klibrate=klibrate.exe -d"%BaseFolder%\%%j\SanXoT\%%i\additional_data\Scans_uncalibrated.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\S2P_RelationsFile.xls" -p"%BaseFolder%\%%j\SanXoT\%%i\data" -aS2P_inOUTs_calibrated -o"scan.xls" -g

set sanxotS2P_in_outs=sanxot.exe -aS2P_inOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"scan.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\S2P_RelationsFile.xls" -g --tags=""
set sanxotsieveSP=sanxotsieve.exe -aS2POuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"scan.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\S2P_RelationsFile.xls" -f0.01 -V"S2P_inOuts_infoFile.txt" --oldway
set sanxotS2P_no_outs=sanxot.exe -aS2P_noOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"scan.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\data\S2POuts_cleaned.xls" -o"peptide.xls" -g -V"S2P_inOuts_infoFile.txt" -f

set sanxotP2Q_in_outs=sanxot.exe -aP2Q_inOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"peptide.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\P2Q_RelationsFile.xls" -g --tags=""
set sanxotsievePQ=sanxotsieve.exe -aP2QOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"peptide.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\P2Q_RelationsFile.xls" -f0.01 -V"P2Q_inOuts_infoFile.txt" --oldway
set sanxotP2Q_no_outs=sanxot.exe -aP2Q_noOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"peptide.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\data\P2QOuts_cleaned.xls" -o"protein.xls" -g -V"P2Q_inOuts_infoFile.txt" -f

set sanxotQ2C_in_outs=sanxot.exe -aQ2C_inOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"protein.xls" -r%Q2CRelationFile% -g --tags=""
set sanxotsieveQC=sanxotsieve.exe -aQ2COuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"protein.xls" -r%Q2CRelationFile% -f0.01 -V"Q2C_inOuts_infoFile.txt" --oldway
set sanxotQ2C_no_outs=sanxot.exe -aQ2C_noOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"protein.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\data\Q2COuts_cleaned.xls" -o"category.xls" -g -V"Q2C_inOuts_infoFile.txt" -f

set sanxotQ2A=sanxot.exe -aQ2A -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"protein.xls" -C -V"Q2C_inOuts_infoFile.txt" -f -g --tags=""

set sanxotC2A=sanxot.exe -aC2A -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"category.xls" -C -v0 -f -g --tags=""

set sanxotP2A_in_outs=sanxot.exe -aP2A_inOuts -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"peptide.xls" -C -g --tags=""

for %%j in (%Experiments%) do (
for %%i in (%Tags%) do (
	if not exist "%BaseFolder%\%%j\SanXoT\%%i\data" md "%BaseFolder%\%%j\SanXoT\%%i\data"
	if not exist "%BaseFolder%\%%j\SanXoT\%%i\additional_data" md "%BaseFolder%\%%j\SanXoT\%%i\additional_data"
	start "CALCULATION_%%i" cmd.exe /C "(%aljamiaSData% & %aljamiaS2PRels% & %aljamiaP2QRels% & %klibrate% & %sanxotS2P_in_outs% & %sanxotsieveSP% & %sanxotS2P_no_outs% & %sanxotP2Q_in_outs% & %sanxotsievePQ% & %sanxotP2Q_no_outs% & %sanxotQ2C_in_outs% & %sanxotsieveQC% & %sanxotQ2C_no_outs% & %sanxotQ2A% & %sanxotC2A% & %sanxotP2A_in_outs%)"
	))
	
	:wait_loop2
	for %%j in (%Experiments%) do (
	for %%i in (%Tags%) do (
	if not exist "%BaseFolder%\%%j\SanXoT\%%i\data\P2A_inOuts_outGraph.png" goto wait_loop2
	))
	
set aljamiaSData_ABS=aljamia.exe -x"%BaseFolder%\%%j\Pre-SanXoT\%Data%" -p"%BaseFolder%\%%j\SanXoT\%%i\additional_data" -o"Scans_uncalibrated_ABS.xls" -aS2P_inOUTs_uncalibrated -i"[Raw_FirstScan]-[Charge]" -j"[Xs_%%i_%ControlTag%]" -k"[Vs_%%i_ABS]" -R1

set klibrate_ABS=klibrate.exe -d"%BaseFolder%\%%j\SanXoT\%%i\additional_data\Scans_uncalibrated_ABS.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\S2P_RelationsFile.xls" -p"%BaseFolder%\%%j\SanXoT\%%i\data" -aS2P_ABS_K -o"scan_ABS.xls" -g -v0 -k1 -f

set sanxotS2P_ABS=sanxot.exe -aS2P_ABS -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"scan_ABS.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\S2P_RelationsFile.xls" -g -v0 -f -o"peptide_ABS.xls"

set sanxotP2Q_ABS=sanxot.exe -aP2Q_ABS -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"peptide_ABS.xls" -r"%BaseFolder%\%%j\SanXoT\%%i\additional_data\P2Q_RelationsFile.xls" -g -v0 -f -o"protein_ABS.xls"

set sanxotQ2A_ABS=sanxot.exe -aQ2A_ABS -p"%BaseFolder%\%%j\SanXoT\%%i\data" -d"protein_ABS.xls" -C -g -v0 -f -o"All_ABS.xls"

for %%j in (%Experiments%) do (
for %%i in (%Tags%) do (
	if not exist "%BaseFolder%\%%j\Absolute_Quantification" md "%BaseFolder%\%%j\Absolute_Quantification"
	start "CALCULATION_%%i" cmd.exe /C "(%aljamiaSData_ABS% & %klibrate_ABS% & %sanxotS2P_ABS% & %sanxotP2Q_ABS% & %sanxotQ2A_ABS%)"
	))
	
	:wait_loop3
	for %%j in (%Experiments%) do (
	for %%i in (%Tags%) do (
	if not exist "%BaseFolder%\%%j\SanXoT\%%i\data\All_ABS.xls" goto wait_loop3
	))

cd "%BaseFolder%"

S:

"C:\Program Files\R\R-3.2.3\bin\R.exe" -f "C:\Users\fgarcia\Desktop\Integrator\standalone exes\Join_Abs_Rel_Quantification.R" --slave

set /p IntegrationName=Integration name:

set /p integration_opt=Execute Integration (Y/N):

cd "C:\Users\fgarcia\Desktop\Integrator\standalone exes"

C:

set cardenio=cardenio.exe -t"%baseFolder%\Integration\%%i_Tag_file.txt" -p"%baseFolder%\Integration\%%i" -a"%%i"

set sanxotQ2e_in_outs_integration=sanxot.exe -d"%baseFolder%\Integration\%%i\%%i_newData.txt" -r"%baseFolder%\Integration\%%i\%%i_newRels.txt" -a%%i_inOUT -g -m1000 -v0 --emergencyvariance
set sanxotsieveQ2e_integration=sanxotsieve.exe -d"%baseFolder%\Integration\%%i\%%i_newData.txt" -r"%baseFolder%\Integration\%%i\%%i_newRels.txt" -V"%baseFolder%\Integration\%%i\%%i_inOUT_infoFile.txt" --oldway
set sanxotQ2e_no_outs_integration=sanxot.exe -d"%baseFolder%\Integration\%%i\%%i_newData.txt" -r"%baseFolder%\Integration\%%i\%%i_newData_cleaned.xls" -V"%baseFolder%\Integration\%%i\%%i_inOUT_infoFile.txt" -a%%i_noOUT -f -o"Protein_integrated.xls" -g

set sanxotQe2C_in_outs_integration=sanxot.exe -a%%i_Q2C_inOuts -p"%baseFolder%\Integration\%%i" -d"%baseFolder%\Integration\%%i\Protein_integrated.xls" -r%Q2CRelationFile% -g --tags=""
set sanxotsieveQe2C_integration=sanxotsieve.exe -a%%i_Q2COuts -p"%baseFolder%\Integration\%%i" -d"%baseFolder%\Integration\%%i\Protein_integrated.xls" -r%Q2CRelationFile% -f0.01 -V"%%i_Q2C_inOuts_infoFile.txt" --oldway
set sanxotQe2C_no_outs_integration=sanxot.exe -a%%i_Q2C_noOuts -p"%baseFolder%\Integration\%%i" -d"%baseFolder%\Integration\%%i\Protein_integrated.xls" -r"%baseFolder%\Integration\%%i\%%i_Q2COuts_cleaned.xls" -V"%%i_Q2C_inOuts_infoFile.txt" -o"Category_integrated.xls" -f -g

set sanxotQe2A_integration=sanxot.exe -a%%i_Q2A -p"%baseFolder%\Integration\%%i" -d"%baseFolder%\Integration\%%i\Protein_integrated.xls" -C -g --tags=""

set sanxotCe2A_integration=sanxot.exe -a%%i_C2A -p"%baseFolder%\Integration\%%i" -d"%baseFolder%\Integration\%%i\Category_integrated.xls" -C -g --tags=""

if %integration_opt% EQU y (
for %%i in (%IntegrationName%) do (
	if not exist "%BaseFolder%\Integration\%%i" md "%BaseFolder%\Integration\%%i"
	start "INTEGRATION_%%i" cmd.exe /C "(%cardenio% & %sanxotQ2e_in_outs_integration% & %sanxotsieveQ2e_integration% & %sanxotQ2e_no_outs_integration% & %sanxotQe2C_in_outs_integration% & %sanxotsieveQe2C_integration% & %sanxotQe2C_no_outs_integration% & %sanxotQe2A_integration% & %sanxotCe2A_integration%)"
	))

cd "%BaseFolder%"

S:

set /p compilator_opt=Execute Compilate all data (Y/N):

set Compilate_all_data="C:\Program Files\R\R-3.2.3\bin\R.exe" -f "C:\Users\fgarcia\Desktop\Integrator\standalone exes\Compilator_all_data.R" --slave

if %compilator_opt% EQU y (
	start "Compilate ALL Data" cmd.exe /C "(%Compilate_all_data%)"
	)
	
