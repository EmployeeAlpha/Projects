<#
    NemesisC64 Auditor — verify-tor.ps1
    Quick network test to check Tor connectivity and IP identity.
#>

Write-Host "=== Verifying Tor connectivity ==="
$TorProxy = "socks5h://127.0.0.1:9050"
$TestUrl  = "https://check.torproject.org/api/ip"

try {
    Write-Host "Querying $TestUrl via Tor proxy ($TorProxy)..."
    $Response = Invoke-WebRequest -Uri $TestUrl -Proxy $TorProxy -UseBasicParsing -TimeoutSec 15
    if ($Response.StatusCode -eq 200) {
        $json = $Response.Content | ConvertFrom-Json
        Write-Host "IP Address: $($json.IP)"
        if ($json.IsTor -eq $true) {
            Write-Host "✅ Connection appears to be through Tor."
        } else {
            Write-Host "⚠️  Tor proxy reachable, but IP not recognized as Tor exit node."
        }
    } else {
        Write-Host "❌ HTTP error: $($Response.StatusCode)"
    }
} catch {
    Write-Host "❌ Error testing Tor connectivity: $($_.Exception.Message)"
}
