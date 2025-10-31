using System;
using System.Collections.ObjectModel;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using Microsoft.Win32;

namespace WpfApp
{
    public partial class MainWindow : Window
    {
        // Bindable collection for the Findings ListView
        public ObservableCollection<Finding> Findings { get; } = new ObservableCollection<Finding>();

        // Paths
        private readonly string _appBase;
        private readonly string _assetsDir;
        private readonly string _reportsDir;
        private readonly string _logsDir;
        private readonly string _pythonDir;
        private readonly string _runnerPath;

        public MainWindow()
        {
            InitializeComponent();

            _appBase   = AppContext.BaseDirectory;
            _assetsDir = Path.Combine(_appBase, "assets");
            _reportsDir= Path.Combine(_appBase, "reports");
            _logsDir   = Path.Combine(_appBase, "logs");
            _pythonDir = Path.Combine(_appBase, "python");
            _runnerPath= Path.Combine(_pythonDir, "runner.py");

            Directory.CreateDirectory(_reportsDir);
            Directory.CreateDirectory(_logsDir);

            lvFindings.ItemsSource = Findings;

            // Wire up events
            btnScan.Click += BtnScan_Click;
            btnOpenReports.Click += (s, e) => OpenFolder(_reportsDir);
            btnOpenLogs.Click += (s, e) => OpenFolder(_logsDir);
            btnInfo.Click += BtnInfo_Click;

            btnSaveReport.Click += BtnSaveReport_Click;
            btnCopySummary.Click += BtnCopySummary_Click;
            btnClear.Click += (s, e) => { txtOutput.Clear(); Findings.Clear(); lblStatus.Text = "Cleared."; progress.Value = 0; };

            // Load footer ASCII (non-blocking)
            _ = LoadAsciiFooterAsync();
        }

        // ========== UI Event Handlers ==========

        private async void BtnScan_Click(object sender, RoutedEventArgs e)
        {
            Findings.Clear();
            txtOutput.Clear();
            lblStatus.Text = "Starting audit…";
            progress.Value = 10;

            try
            {
                var request = new AuditorRequest
                {
                    Query = txtQuery.Text?.Trim(),
                    UseTor = chkUseTor.IsChecked == true,
                    WebhookUrl = string.IsNullOrWhiteSpace(txtWebhook.Text) ? null : txtWebhook.Text.Trim(),
                    WebhookSecret = string.IsNullOrWhiteSpace(txtWebhookSecret.Text) ? null : txtWebhookSecret.Text.Trim(),
                    EmailTo = string.IsNullOrWhiteSpace(txtEmailTo.Text) ? null : txtEmailTo.Text.Trim(),
                    EmailSubject = string.IsNullOrWhiteSpace(txtEmailSubject.Text) ? null : txtEmailSubject.Text.Trim(),
                    AttachReport = chkAttachReport.IsChecked == true
                };

                progress.Value = 20;
                AppendOutput("Preparing Python bridge…");

                var result = await RunPythonAsync(request);
                progress.Value = 80;

                if (result != null)
                {
                    // Summary/log text
                    if (!string.IsNullOrWhiteSpace(result.Summary))
                    {
                        AppendOutput("=== SUMMARY ===");
                        AppendOutput(result.Summary);
                        AppendOutput("");
                    }

                    // Findings
                    if (result.Findings != null)
                    {
                        foreach (var f in result.Findings)
                        {
                            Findings.Add(f);
                        }
                        AppendOutput($"Added {Findings.Count} finding(s) to the grid.");
                    }

                    // Any extra log lines
                    if (result.LogLines != null)
                    {
                        AppendOutput("=== LOG ===");
                        foreach (var line in result.LogLines)
                            AppendOutput(line);
                    }

                    lblStatus.Text = "Audit complete.";
                    progress.Value = 100;
                }
                else
                {
                    lblStatus.Text = "No result from Python.";
                }
            }
            catch (Exception ex)
            {
                lblStatus.Text = "Audit failed.";
                AppendOutput("ERROR: " + ex.Message);
                MessageBox.Show(ex.Message, "Run Audit Failed", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void BtnInfo_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // If InfoWindow exists in project, open it. If not yet created, show a friendly note.
                var type = Type.GetType("WpfApp.InfoWindow");
                if (type != null)
                {
                    var win = (Window)Activator.CreateInstance(type)!;
                    win.Owner = this;
                    win.ShowDialog();
                }
                else
                {
                    MessageBox.Show(
                        "Info window not built yet. We'll add it right after the main window logic.\n\n" +
                        "It will render /assets/info_text.html with styling.",
                        "Info / About",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information
                    );
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to open Info window:\n" + ex.Message, "Info", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void BtnSaveReport_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var dlg = new SaveFileDialog
                {
                    Title = "Save Auditor Report",
                    Filter = "Text Report (*.txt)|*.txt|JSON (*.json)|*.json",
                    FileName = $"auditor_report_{DateTime.Now:yyyyMMdd_HHmmss}"
                };
                if (dlg.ShowDialog(this) == true)
                {
                    if (Path.GetExtension(dlg.FileName).Equals(".json", StringComparison.OrdinalIgnoreCase))
                    {
                        // Serialize current findings + output into JSON
                        var payload = new
                        {
                            generated_at = DateTime.UtcNow,
                            findings = Findings,
                            output_text = txtOutput.Text
                        };
                        var json = JsonSerializer.Serialize(payload, new JsonSerializerOptions { WriteIndented = true });
                        File.WriteAllText(dlg.FileName, json, Encoding.UTF8);
                    }
                    else
                    {
                        // Plain text
                        File.WriteAllText(dlg.FileName, txtOutput.Text, Encoding.UTF8);
                    }
                    lblStatus.Text = $"Report saved: {dlg.FileName}";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Failed to save report:\n" + ex.Message, "Save Report", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void BtnCopySummary_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Clipboard.SetText(txtOutput.Text);
                lblStatus.Text = "Summary copied to clipboard.";
            }
            catch (Exception ex)
            {
                MessageBox.Show("Could not copy to clipboard:\n" + ex.Message, "Copy Summary", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        // ========== Helpers ==========

        private void AppendOutput(string line)
        {
            txtOutput.AppendText(line + Environment.NewLine);
            txtOutput.ScrollToEnd();
        }

        private void OpenFolder(string path)
        {
            try
            {
                if (!Directory.Exists(path))
                    Directory.CreateDirectory(path);

                using var p = new Process();
                p.StartInfo = new ProcessStartInfo
                {
                    FileName = "explorer.exe",
                    Arguments = $"\"{path}\"",
                    UseShellExecute = true
                };
                p.Start();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to open folder:\n" + ex.Message, "Open Folder", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private async Task LoadAsciiFooterAsync()
        {
            try
            {
                var footerPath = Path.Combine(_assetsDir, "ascii_footer.txt");
                if (File.Exists(footerPath))
                {
                    using var fs = File.OpenRead(footerPath);
                    using var sr = new StreamReader(fs, Encoding.UTF8);
                    var text = await sr.ReadToEndAsync();
                    txtAsciiFooter.Text = text;
                }
            }
            catch
            {
                // Non-fatal; ignore
            }
        }

        // Runs python\runner.py and returns parsed result
        private async Task<AuditorResult?> RunPythonAsync(AuditorRequest request)
        {
            if (!File.Exists(_runnerPath))
                throw new FileNotFoundException("Python runner not found.", _runnerPath);

            var requestJson = JsonSerializer.Serialize(request, new JsonSerializerOptions { DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull });
            var tempInput = Path.Combine(_logsDir, $"request_{DateTime.Now:yyyyMMdd_HHmmss}.json");
            var tempOutput = Path.Combine(_logsDir, $"response_{DateTime.Now:yyyyMMdd_HHmmss}.json");
            Directory.CreateDirectory(_logsDir);
            await File.WriteAllTextAsync(tempInput, requestJson, Encoding.UTF8);

            // Try common Python launchers
            string[] candidates =
            {
                "py -3",
                "py",
                "python",
                "python3"
            };

            string? chosen = null;
            foreach (var c in candidates)
            {
                if (await CanStartPythonAsync(c))
                {
                    chosen = c;
                    break;
                }
            }

            if (chosen is null)
                throw new InvalidOperationException("No suitable Python interpreter found (tried: py -3, py, python, python3).");

            var args = $"\"{_runnerPath}\" --input \"{tempInput}\" --output \"{tempOutput}\"";
            AppendOutput($"Launching: {chosen} {args}");

            var psi = new ProcessStartInfo
            {
                FileName = chosen.Split(' ')[0],
                Arguments = string.Join(' ', chosen.Contains(' ') ? chosen.Split(' ')[1..] : Array.Empty<string>()) + " " + args,
                WorkingDirectory = _pythonDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            var stdout = new StringBuilder();
            var stderr = new StringBuilder();

            var tcs = new TaskCompletionSource<int>();

            using var proc = new Process { StartInfo = psi, EnableRaisingEvents = true };
            proc.OutputDataReceived += (s, e) => { if (e.Data != null) { stdout.AppendLine(e.Data); } };
            proc.ErrorDataReceived  += (s, e) => { if (e.Data != null) { stderr.AppendLine(e.Data); } };
            proc.Exited += (s, e) => tcs.TrySetResult(proc.ExitCode);

            proc.Start();
            proc.BeginOutputReadLine();
            proc.BeginErrorReadLine();

            var exitCode = await tcs.Task;

            AppendOutput("=== Python STDOUT ===");
            AppendOutput(stdout.ToString());
            if (stderr.Length > 0)
            {
                AppendOutput("=== Python STDERR ===");
                AppendOutput(stderr.ToString());
            }

            if (exitCode != 0)
                throw new InvalidOperationException($"runner.py exited with code {exitCode}");

            if (!File.Exists(tempOutput))
                throw new FileNotFoundException("runner.py did not produce an output file.", tempOutput);

            var json = await File.ReadAllTextAsync(tempOutput, Encoding.UTF8);
            var result = JsonSerializer.Deserialize<AuditorResult>(json, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            return result;
        }

        private static async Task<bool> CanStartPythonAsync(string cmd)
        {
            try
            {
                var first = cmd.Split(' ')[0];
                var rest = cmd.Contains(' ') ? string.Join(' ', cmd.Split(' ')[1..]) : "";
                var psi = new ProcessStartInfo
                {
                    FileName = first,
                    Arguments = string.IsNullOrWhiteSpace(rest) ? "--version" : rest + " --version",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };
                using var p = new Process { StartInfo = psi };
                p.Start();
                await p.WaitForExitAsync();
                return p.ExitCode == 0;
            }
            catch { return false; }
        }
    }

    // ========== Data Contracts ==========

    public class AuditorRequest
    {
        [JsonPropertyName("query")]
        public string? Query { get; set; }

        [JsonPropertyName("use_tor")]
        public bool UseTor { get; set; }

        [JsonPropertyName("webhook_url")]
        public string? WebhookUrl { get; set; }

        [JsonPropertyName("webhook_secret")]
        public string? WebhookSecret { get; set; }

        [JsonPropertyName("email_to")]
        public string? EmailTo { get; set; }

        [JsonPropertyName("email_subject")]
        public string? EmailSubject { get; set; }

        [JsonPropertyName("attach_report")]
        public bool AttachReport { get; set; }
    }

    public class AuditorResult
    {
        [JsonPropertyName("summary")]
        public string? Summary { get; set; }

        [JsonPropertyName("findings")]
        public Finding[]? Findings { get; set; }

        [JsonPropertyName("log_lines")]
        public string[]? LogLines { get; set; }
    }

    public class Finding
    {
        [JsonPropertyName("type")]
        public string? Type { get; set; }

        [JsonPropertyName("detail")]
        public string? Detail { get; set; }

        [JsonPropertyName("location")]
        public string? Location { get; set; }
    }
}
