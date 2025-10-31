using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows;

namespace WpfApp
{
    public partial class InfoWindow : Window
    {
        private readonly string _appBase;
        private readonly string _assetsDir;
        private readonly string _htmlPath;

        public InfoWindow()
        {
            InitializeComponent();

            _appBase  = AppContext.BaseDirectory;
            _assetsDir= Path.Combine(_appBase, "assets");
            _htmlPath = Path.Combine(_assetsDir, "info_text.html");

            btnClose.Click += (s, e) => Close();
            btnOpenFile.Click += (s, e) => OpenAssetsFolder();

            LoadHtml();
        }

        private void LoadHtml()
        {
            try
            {
                Directory.CreateDirectory(_assetsDir);

                if (!File.Exists(_htmlPath))
                {
                    // Seed a minimal placeholder so the window always shows something
                    var placeholder = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                      <meta charset="utf-8">
                      <title>NemesisC64 Auditor — Info</title>
                      <style>
                        body { background:#1e1f24; color:#ececec; font-family:Segoe UI, Arial, sans-serif; margin:20px; }
                        h1,h2 { color:#4b77be; }
                        code, pre { background:#262833; padding:2px 6px; border-radius:4px; }
                        a { color:#00c2a8; }
                        .note { color:#b8b8b8; }
                        .card { background:#262833; border:1px solid #3a3d45; padding:16px; border-radius:8px; }
                      </style>
                    </head>
                    <body>
                      <h1>NemesisC64 Auditor</h1>
                      <div class="card">
                        <p>This window renders <code>/assets/info_text.html</code>. Replace that file with your own styled content.</p>
                        <p class="note">Tip: Click “Open File Location” to drop in your real HTML.</p>
                      </div>
                    </body>
                    </html>
                    """;
                    File.WriteAllText(_htmlPath, placeholder, Encoding.UTF8);
                }

                // Navigate using file:// URI so WebBrowser loads local HTML
                var uri = new Uri(_htmlPath);
                browser.Navigate(uri);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Failed to load info HTML:\n" + ex.Message, "Info", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void OpenAssetsFolder()
        {
            try
            {
                if (!Directory.Exists(_assetsDir))
                    Directory.CreateDirectory(_assetsDir);

                Process.Start(new ProcessStartInfo
                {
                    FileName = "explorer.exe",
                    Arguments = $"\"{_assetsDir}\"",
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                MessageBox.Show("Unable to open assets folder:\n" + ex.Message, "Open Folder", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }
    }
}
