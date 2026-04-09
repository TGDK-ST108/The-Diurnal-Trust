using DotNetHost.Native;
using System.Reflection;
using System.Runtime.InteropServices;

internal static class Program
{
    static void Main()
    {
        NativeResolver.Configure();

        var sum = RustNative.RsAdd(20, 22);
        Console.WriteLine($"rs_add => {sum}");

        var result = RustNative.ProcessText("rust.net setup protocol");
        Console.WriteLine(result);
    }
}

internal static class NativeResolver
{
    public static void Configure()
    {
        NativeLibrary.SetDllImportResolver(
            Assembly.GetExecutingAssembly(),
            static (libraryName, assembly, searchPath) =>
            {
                var baseDir = AppContext.BaseDirectory;

                string fileName = RuntimeInformation.IsOSPlatform(OSPlatform.Windows)
                    ? "rust_core.dll"
                    : RuntimeInformation.IsOSPlatform(OSPlatform.OSX)
                        ? "librust_core.dylib"
                        : "librust_core.so";

                var candidate = Path.Combine(baseDir, fileName);

                if (File.Exists(candidate))
                {
                    return NativeLibrary.Load(candidate);
                }

                return IntPtr.Zero;
            });
    }
}
