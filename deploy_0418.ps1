$ErrorActionPreference = "Continue"
Set-Location "G:\PyBOT\Projects\wio_nord_bot"
$env:GIT_SSH_COMMAND = "C:/Windows/System32/OpenSSH/ssh.exe"
git add -A
git reset -q HEAD -- _rel.py _rel.txt 2>$null
git commit -m "feat: v0.41.18 - lab to treasury, kvp 5, hub dodge fix, tiers to 10, tree 6+, talisman/clan_cape, spoiled fish merge"
git tag v0.41.18
git push server main --tags
git push origin main --tags
git log --oneline -1
git status --short
