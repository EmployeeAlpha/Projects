using System;
using System.Windows;

namespace WpfApp
{
    public partial class App : Application
    {
        public App()
        {
            // Global application constructor
            this.DispatcherUnhandledException += App_DispatcherUnhandledException;
            AppDomain.CurrentDomain.UnhandledException += CurrentDomain_UnhandledException;
        }

        private void App_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            MessageBox.Show(
                "An unexpected error occurred:\n\n" + e.Exception.Message,
                "NemesisC64 Auditor",
                MessageBoxButton.OK,
                MessageBoxImage.Error
            );
            e.Handled = true;
        }

        private void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            if (e.ExceptionObject is Exception ex)
            {
                MessageBox.Show(
                    "A critical error occurred:\n\n" + ex.Message,
                    "NemesisC64 Auditor",
                    MessageBoxButton.OK,
                    MessageBoxImage.Stop
                );
            }
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // You can place future initialization logic here
            // e.g., loading configuration or verifying Python bridge availability
        }
    }
}
