#include "USTAF_ADL_Tokenizer.h"
#include "PKG.cpp"

namespace smirf {
    void enforce_pkg_gate(const std::string& token_id, const std::string& key) {
        USTAF_ADL_Tokenizer tokenizer;
        tokenizer.register_token(token_id, PRIVATE, 600, key);
        PyramidKernelGateway pkg(tokenizer);

        if (pkg.authorize(token_id, key)) {
            pkg.enforce_seal();
            std::cout << "[SMIRF] PKG access granted for diagnostics.\n";
        } else {
            std::cout << "[SMIRF] PKG access denied.\n";
        }
    }
}