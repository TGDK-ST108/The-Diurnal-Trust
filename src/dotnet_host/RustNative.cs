using System.Runtime.InteropServices;
using System.Text;

namespace DotNetHost.Native;

internal static partial class RustNative
{
#if WINDOWS
    private const string LibName = "rust_core";
#elif LINUX
    private const string LibName = "librust_core";
#elif OSX
    private const string LibName = "librust_core";
#else
    private const string LibName = "rust_core";
#endif

    [LibraryImport(LibName, EntryPoint = "rs_add")]
    internal static partial int RsAdd(int left, int right);

    [LibraryImport(LibName, EntryPoint = "rs_process_text", StringMarshalling = StringMarshalling.Utf8)]
    internal static partial IntPtr RsProcessText(string input);

    [LibraryImport(LibName, EntryPoint = "rust_string_free")]
    internal static partial void RustStringFree(IntPtr ptr);

    internal static string ProcessText(string input)
    {
        var ptr = RsProcessText(input);
        if (ptr == IntPtr.Zero)
            throw new InvalidOperationException("Rust returned null.");

        try
        {
            return Marshal.PtrToStringUTF8(ptr) ?? string.Empty;
        }
        finally
        {
            RustStringFree(ptr);
        }
    }
}
