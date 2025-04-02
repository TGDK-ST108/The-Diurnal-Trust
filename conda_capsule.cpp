#include <iostream>
#include "Enzo.h"
#include "USTAF_ADL_Tokenizer.h"
#include "PKG.cpp"

class CodenameCondaCapsule {
public:
    static void deploy_capsule(const std::string& token, const std::string& key) {
        USTAF_ADL_Tokenizer tokenizer;
        tokenizer.register_token(token, PRIVATE, 1200, key);
        PyramidKernelGateway pkg(tokenizer);

        if (!pkg.authorize(token, key)) {
            std::cout << "[CSC] Capsule lockdown. Unauthorized entry." << std::endl;
            return;
        }

        pkg.enforce_seal();
        std::cout << "[CSC] Codename CONDA capsule active. Enzo now sealed within quantum perimeter." << std::endl;
    }
};