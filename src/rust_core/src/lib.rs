use std::ffi::{CStr, CString, c_char};

/// SAFETY:
/// The symbol name must be unique in the final link graph.
#[unsafe(no_mangle)]
pub extern "C" fn rs_add(left: i32, right: i32) -> i32 {
    left + right
}

/// Accepts a nul-terminated UTF-8-ish C string and returns a newly allocated
/// C string that must be freed by rust_string_free().
///
/// SAFETY:
/// - `input` must be a valid, non-null pointer to a nul-terminated C string.
/// - Caller must later pass the returned pointer to rust_string_free().
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rs_process_text(input: *const c_char) -> *mut c_char {
    if input.is_null() {
        return CString::new("ERR:null input").unwrap().into_raw();
    }

    let c_str = unsafe { CStr::from_ptr(input) };
    let text = c_str.to_string_lossy();

    let output = format!("rust_core processed: {}", text.to_uppercase());
    CString::new(output).unwrap().into_raw()
}

/// Frees a string previously allocated by rs_process_text().
///
/// SAFETY:
/// - `ptr` must be either null or a pointer returned by rs_process_text().
/// - Do not free the same pointer twice.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn rust_string_free(ptr: *mut c_char) {
    if ptr.is_null() {
        return;
    }

    unsafe {
        drop(CString::from_raw(ptr));
    }
}
