CD "C:\Users\fgarcia\Desktop\pRatio_CMD"

C:

set pRatio=pRatio.exe -t "%BaseFolder%\%%i\MSFs_dir\%%j\%%j_%%k_dir" -d "%BaseFolder%\%%i\MSFs_inv\%%j\%%j_%%k_inv" -pd 2.x -o "%BaseFolder%\%%i\MSFs_dir\%%j\%%j_%%k_dir" -fc .01 -dm five -dt 20 -n 229.162932 -q xcorr -fm mixed

for %%i in (MSFs_MKRPWYdioxidation MSFs_MKRPWYoxidation) do (
for %%j in (TMT1 TMT2 TMT3) do (
for %%k in (ALL FR1 FR2 FR3 FR4 FR5 FR6 FR7 FR8 ALL_BIS FR1_BIS FR2_BIS FR3_BIS FR4_BIS FR5_BIS FR6_BIS FR7_BIS FR8_BIS ALL_MIX) do (

	start "pRatio_%%k" cmd.exe /K "(%pRatio%)"
	)))