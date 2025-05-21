-- TETRAFI :: Hardware Acceleration for TETRADEN
-- Format: LuaJIT for Termux

local ffi = require("ffi")
local bit = require("bit")

ffi.cdef[[
    int getauxval(unsigned long type);
    typedef unsigned int uint32_t;
    typedef unsigned long size_t;
    void *memcpy(void *dest, const void *src, size_t n);
]]

local function detect_hw_flags()
    local fd = io.open("/proc/cpuinfo", "r")
    local flags = fd:read("*all")
    fd:close()
    return flags
end

function is_neon_supported()
    return detect_hw_flags():match("neon") ~= nil
end

function fast_xor(input, key)
    local out = {}
    for i = 1, #input do
        local a = input:byte(i)
        local b = key:byte((i - 1) % #key + 1)
        table.insert(out, string.char(bit.bxor(a, b)))
    end
    return table.concat(out)
end

function hardware_entropy()
    local f = io.open("/dev/hw_random", "rb") or io.open("/dev/urandom", "rb")
    local data = f:read(128)
    f:close()
    return data
end

-- Fused Hardware Cipher Pattern
function tetrafi_vector_seal(input, key)
    local entropy = hardware_entropy()
    local mixed = fast_xor(input .. entropy, key)
    return mixed
end

-- Example
if is_neon_supported() then
    print("[TETRAFI] :: NEON instructions detected.")
else
    print("[TETRAFI] :: Fallback mode (no NEON).")
end