@echo off
rem ==========================================================================================
rem  aizen-upgrade.bat - nang cap Aizen cho mot du an dang chay, an toan (Windows cmd / PowerShell)
rem
rem  Chay tu thu muc du an (hoac bat ky thu muc con nao):
rem    aizen-upgrade.bat check   [base]   chi kiem tra, KHONG doi gi - chay cai nay truoc
rem    aizen-upgrade.bat upgrade [base]   sao luu, go file AI khoi git, cap nhat skill, cai hook
rem    aizen-upgrade.bat finish  [base]   chay tiep buoc 4-6 khi upgrade dung sau buoc cap nhat skill
rem    aizen-upgrade.bat after-merge [base]  sau khi merge PR "untrack": ve base, pull, khoi phuc skill
rem    aizen-upgrade.bat restore          chep lai ban skill v26 da cai (khi checkout lam mat/ghi de)
rem    aizen-upgrade.bat rollback         tra skill va .aizen ve ban truoc khi nang cap
rem  base mac dinh: develop
rem
rem  Dat file NGOAI thu muc du an (vd. thu muc cha), neu khong git thay file moi va cay khong sach.
rem  Script khong bao gio force-push, khong viet lai lich su, khong xoa nhanh tren GitHub.
rem  Thong bao khong dau de cmd hien thi dung tren moi may.
rem ==========================================================================================
setlocal EnableExtensions EnableDelayedExpansion

set "MODE=%~1"
if "%MODE%"=="" set "MODE=check"
set "BASE=%~2"
if "%BASE%"=="" set "BASE=develop"
set "BRANCH=chore/untrack-agent-files"
set "AI_FILES=.agents .claude .cursor .gemini .windsurf .codex .kiro AGENTS.md CLAUDE.md GEMINI.md .mcp.json skills-lock.json graphify-out"

rem ---- cong cu va thu muc du an ---------------------------------------------------------------
for %%t in (git uv npx) do (
  where %%t >nul 2>&1 || (echo [X] Khong tim thay %%t tren PATH. & exit /b 1)
)
for /f "delims=" %%r in ('git rev-parse --show-toplevel 2^>nul') do set "ROOT=%%r"
if not defined ROOT (echo [X] Day khong phai thu muc git. & exit /b 1)
cd /d "%ROOT%"
for /f "delims=" %%d in ('git rev-parse --absolute-git-dir') do set "GITDIR=%%d"
for %%I in (.) do set "REPO=%%~nxI"
set "BKFILE=%GITDIR%\aizen-upgrade-backup.txt"

set "CORE="
if exist ".agents\skills\aizen-core\manifest.json" set "CORE=.agents\skills\aizen-core"
if not defined CORE if exist ".claude\skills\aizen-core\manifest.json" set "CORE=.claude\skills\aizen-core"

if /i "%MODE%"=="check"       goto :check
if /i "%MODE%"=="upgrade"     goto :upgrade
if /i "%MODE%"=="after-merge" goto :aftermerge
if /i "%MODE%"=="restore"     goto :restore
if /i "%MODE%"=="finish"      goto :finish
if /i "%MODE%"=="rollback"    goto :rollback
echo Cach dung: aizen-upgrade.bat check^|upgrade^|finish^|after-merge^|restore^|rollback [base]
exit /b 1

rem ==========================================================================================
:check
echo.
echo === Du an: %REPO%   base: %BASE% ===
call :report
echo.
echo Neu muc nao co [CHU Y] thi xu ly truoc, roi chay: aizen-upgrade.bat upgrade %BASE%
exit /b 0

:report
for /f "delims=" %%b in ('git branch --show-current') do echo Nhanh hien tai : %%b
if defined CORE (
  for /f "tokens=2 delims=:," %%v in ('findstr /c:"\"version\"" "%CORE%\manifest.json"') do echo Aizen dang cai : %%~v  [%CORE%]
) else (
  echo [CHU Y] Khong thay aizen-core trong .agents\skills hoac .claude\skills
)
git rev-parse --verify --quiet "refs/heads/%BASE%" >nul || echo [CHU Y] Khong co nhanh %BASE% o may - truyen ten base dung o tham so thu 2
set "DIRTY="
for /f "delims=" %%x in ('git status --porcelain') do set "DIRTY=1"
if defined DIRTY (echo [CHU Y] Con thay doi chua commit - commit hoac stash truoc) else (echo [ok] Cay lam viec sach)
set "TRACKED="
for /f "delims=" %%f in ('git ls-files %AI_FILES%') do set "TRACKED=1"
if defined TRACKED (
  echo [CHU Y] File AI dang duoc git theo doi - buoc upgrade se go chung khoi git, file van con tren may:
  for %%p in (%AI_FILES%) do (
    git ls-files --error-unmatch "%%p" >nul 2>&1 && echo       %%p
  )
) else (
  echo [ok] Khong co file AI nao trong git
)
echo Commit chua push co ma task (vd. TET-12) hoac dong dong tac gia AI - pre-push se kiem lai:
set "BAD="
for /f "delims=" %%c in ('git log --branches --not --remotes -E "--grep=[A-Z][A-Z0-9]+-[0-9]+" "--grep=Co-Authored-By" "--format=      %%h %%s"') do (
  echo %%c
  set "BAD=1"
)
if defined BAD (echo [CHU Y] Sua bang git rebase -i ^> reword, hoac push xong truoc khi nang cap) else (echo       khong co)
echo Run Aizen dang do - nen lam xong hoac dung truoc khi nang cap:
set "RUNS="
if exist ".aizen\runs\" for /f "delims=" %%r in ('dir /b /ad ".aizen\runs" 2^>nul') do (
  if /i not "%%r"=="init" echo       %%r
  if /i not "%%r"=="init" set "RUNS=1"
)
if not defined RUNS echo       khong co
exit /b 0

rem ==========================================================================================
:upgrade
echo.
echo === Nang cap Aizen v26 - %REPO% ===
call :report
if defined DIRTY (echo [X] Hay commit hoac stash truoc. & exit /b 1)
if not defined CORE (echo [X] Du an chua cai Aizen. & exit /b 1)
git rev-parse --verify --quiet "refs/heads/%BASE%" >nul || (echo [X] Khong co nhanh %BASE%. & exit /b 1)
if defined BAD (
  choice /c YN /m "Co commit chua push se bi chan. Van tiep tuc"
  if errorlevel 2 exit /b 1
)
if defined RUNS (
  echo Run dang do van chay tiep sau nang cap, nhung nhanh cu cua no con theo doi .agents/.claude:
  echo checkout nhanh do se ghi de skill v26 bang ban cu - khi do chay "aizen-upgrade.bat restore".
  choice /c YN /m "Da dong phien agent va muon tiep tuc"
  if errorlevel 2 exit /b 1
)

rem ---- 1. sao luu truoc khi doi bat cu gi --------------------------------------------------
for /f %%t in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set "TS=%%t"
set "BK=%USERPROFILE%\aizen-backups\%REPO%-%TS%"
echo [1/6] Sao luu vao %BK%\before
call :copyset "%ROOT%" "%BK%\before" || exit /b 1
> "%BKFILE%" echo %BK%

rem ---- 2. nhanh nghiep vu go file AI khoi git (file van con tren may) ------------------------
echo [2/6] Tao nhanh %BRANCH% tu %BASE% va go file AI khoi git
git switch -q "%BASE%" || exit /b 1
git pull -q --ff-only || (echo [X] Khong pull duoc %BASE% - kiem tra mang/xung dot roi chay lai. & exit /b 1)
git rev-parse --verify --quiet "refs/heads/%BRANCH%" >nul && (git switch -q "%BRANCH%") || (git switch -q -c "%BRANCH%")
git rm -r -q --cached --ignore-unmatch %AI_FILES%
git diff --cached --quiet
if errorlevel 1 (
  git commit -q -m "chore: stop tracking local agent tool files" || exit /b 1
  echo       da commit tren %BRANCH%
) else (
  echo       khong co gi de go - bo qua
)
rem cac file vua go phai van con tren dia; neu checkout lam mat thi lay lai tu ban sao luu
if not exist "%CORE%\manifest.json" call :copyback "%BK%\before" || exit /b 1

rem ---- 3. cap nhat skill -----------------------------------------------------------------
echo [3/6] npx skills update
call npx -y skills update -p || (echo [X] skills update loi - chay "aizen-upgrade.bat rollback" de tra ve ban cu. & exit /b 1)
findstr /r /c:"version.*26[.]" "%CORE%\manifest.json" >nul
if errorlevel 1 (
  echo [X] aizen-core van chua len 26.x - kiem tra PR da merge vao Aizen-Skills main chua.
  exit /b 1
)
:step4

rem ---- 4. hook, rules, exclude ------------------------------------------------------------
echo [4/6] guard.py install
uv run --quiet "%CORE%\scripts\core\guard.py" install || exit /b 1
for %%p in (%AI_FILES%) do (
  set "ENTRY=%%p"
  if exist "%%p\" set "ENTRY=%%p/"
  findstr /x /l /c:"!ENTRY!" "%GITDIR%\info\exclude" >nul 2>&1 || >>"%GITDIR%\info\exclude" echo !ENTRY!
)

rem ---- 5. luu ban v26 da cai de khoi phuc sau khi merge --------------------------------------
echo [5/6] Luu ban da cai vao %BK%\installed
call :copyset "%ROOT%" "%BK%\installed" noaizen || exit /b 1

rem ---- 6. push nhanh untrack ------------------------------------------------------------
echo [6/6] Kiem tra nhanh truoc khi push
git ls-files %AI_FILES% | findstr . >nul && (echo [X] Van con file AI trong git. & exit /b 1)
echo       khong con file AI trong git
choice /c YN /m "Push nhanh %BRANCH% len GitHub ngay"
if errorlevel 2 goto :done_upgrade
git push -u origin "%BRANCH%" || (echo [X] Push bi chan - doc ly do o tren. & exit /b 1)
where gh >nul 2>&1 && (
  choice /c YN /m "Tao PR vao %BASE% bang gh"
  if not errorlevel 2 gh pr create --base "%BASE%" --head "%BRANCH%" --title "chore: stop tracking local agent tool files" --body "Agent files stay on each machine; the repository keeps only the product."
)

:done_upgrade
echo.
echo XONG. Tiep theo:
echo   1. Merge PR %BRANCH% vao %BASE% tren GitHub.
echo   2. Chay: aizen-upgrade.bat after-merge %BASE%
echo   Sao luu: %BK%   - quay lai ban cu: aizen-upgrade.bat rollback
exit /b 0

rem ==========================================================================================
:finish
echo.
echo === Tiep tuc buoc 4-6 (skill da cap nhat) - %REPO% ===
call :loadbk || exit /b 1
if not defined CORE (echo [X] Khong thay aizen-core. & exit /b 1)
goto :step4

:aftermerge
echo.
echo === Sau khi merge - %REPO% ===
call :loadbk || exit /b 1
set "DIRTY="
for /f "delims=" %%x in ('git status --porcelain') do set "DIRTY=1"
if defined DIRTY (echo [X] Con thay doi chua commit. & exit /b 1)
git switch -q "%BASE%" || exit /b 1
git pull -q --ff-only || exit /b 1
git ls-files %AI_FILES% | findstr . >nul && (
  echo [X] %BASE% van theo doi file AI - PR chua merge? Merge xong roi chay lai.
  goto :restore_files
)
git branch -d "%BRANCH%" >nul 2>&1 && echo       da xoa nhanh %BRANCH% o may
goto :restore_files

rem ==========================================================================================
:restore
call :loadbk || exit /b 1
:restore_files
echo Khoi phuc skill v26 tu %BK%\installed
call :copyback "%BK%\installed" || exit /b 1
if exist ".agents\skills\aizen-core\manifest.json" (set "CORE=.agents\skills\aizen-core") else set "CORE=.claude\skills\aizen-core"
uv run --quiet "%CORE%\scripts\core\guard.py" install || exit /b 1
for /f "tokens=2 delims=:," %%v in ('findstr /c:"\"version\"" "%CORE%\manifest.json"') do echo Aizen dang cai: %%~v
echo XONG. Mo phien agent moi; task moi dung: state.py init --task ^<ID^> --goal "..." --slug ^<ten-nghiep-vu^>
exit /b 0

rem ==========================================================================================
:rollback
call :loadbk || exit /b 1
echo Tra skill, rules va .aizen ve ban truoc nang cap tu %BK%\before
choice /c YN /m "Chac chan"
if errorlevel 2 exit /b 1
call :copyback "%BK%\before" || exit /b 1
if exist ".agents\skills\aizen-core\manifest.json" (set "CORE=.agents\skills\aizen-core") else set "CORE=.claude\skills\aizen-core"
uv run --quiet "%CORE%\scripts\core\guard.py" install
echo XONG. Commit tren nhanh %BRANCH% (neu co) van giu nguyen - xoa bang: git branch -D %BRANCH%
exit /b 0

rem ==========================================================================================
:copyset  src dst [noaizen]  - chep .agents .claude skills-lock.json (va .aizen tru worktrees/cache)
setlocal
set "SRC=%~1" & set "DST=%~2"
for %%d in (.agents .claude) do if exist "%SRC%\%%d\" (
  robocopy "%SRC%\%%d" "%DST%\%%d" /E /NFL /NDL /NJH /NJS /NP >nul
  if errorlevel 8 (echo [X] Sao luu %%d loi. & exit /b 1)
)
if exist "%SRC%\skills-lock.json" copy /y "%SRC%\skills-lock.json" "%DST%\skills-lock.json" >nul
if /i not "%~3"=="noaizen" if exist "%SRC%\.aizen\" (
  robocopy "%SRC%\.aizen" "%DST%\.aizen" /E /XD worktrees cache /NFL /NDL /NJH /NJS /NP >nul
  if errorlevel 8 (echo [X] Sao luu .aizen loi. & exit /b 1)
)
endlocal & exit /b 0

:copyback  src  - chep nguoc vao du an (khong xoa file thua)
setlocal
set "SRC=%~1"
if not exist "%SRC%\" (echo [X] Khong thay ban sao luu %SRC% & exit /b 1)
for %%d in (.agents .claude .aizen) do if exist "%SRC%\%%d\" (
  robocopy "%SRC%\%%d" "%ROOT%\%%d" /E /NFL /NDL /NJH /NJS /NP >nul
  if errorlevel 8 (echo [X] Khoi phuc %%d loi. & exit /b 1)
)
if exist "%SRC%\skills-lock.json" copy /y "%SRC%\skills-lock.json" "%ROOT%\skills-lock.json" >nul
endlocal & exit /b 0

:loadbk
if not exist "%BKFILE%" (echo [X] Chua chay "upgrade" o du an nay - khong co ban sao luu. & exit /b 1)
set /p BK=<"%BKFILE%"
exit /b 0
