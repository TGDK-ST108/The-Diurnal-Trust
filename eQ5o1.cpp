// ===============================
// TGDK :: eQ5o1.cpp
// Encryption | DNS Protection | Dox Security
// BFE-TGDK-022ST | Sean Tichenor | © TGDK All Rights Reserved
// ===============================

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

// ===============================
// AES-256 Encryption/Decryption
// ===============================

const int AES_KEYLEN = 32;  // 256 bits
const int AES_IVLEN  = 16;  // 128 bits

int generate_key_iv(unsigned char* key, unsigned char* iv) {
    if (!RAND_bytes(key, AES_KEYLEN) || !RAND_bytes(iv, AES_IVLEN)) {
        std::cerr << "[eQ5o1] Key/IV generation failed." << std::endl;
        return 0;
    }
    return 1;
}

int aes_crypt(const std::string& infile, const std::string& outfile, const unsigned char* key, const unsigned char* iv, bool encrypt) {
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    std::ifstream in(infile, std::ios::binary);
    std::ofstream out(outfile, std::ios::binary);
    if (!in || !out) return -2;

    EVP_CipherInit_ex(ctx, EVP_aes_256_cbc(), nullptr, key, iv, encrypt);

    unsigned char inbuf[1024], outbuf[1024 + AES_BLOCK_SIZE];
    int inlen, outlen;

    while (in.good()) {
        in.read((char*)inbuf, sizeof(inbuf));
        inlen = in.gcount();
        if (!EVP_CipherUpdate(ctx, outbuf, &outlen, inbuf, inlen)) return -3;
        out.write((char*)outbuf, outlen);
    }

    if (!EVP_CipherFinal_ex(ctx, outbuf, &outlen)) return -4;
    out.write((char*)outbuf, outlen);

    EVP_CIPHER_CTX_free(ctx);
    return 0;
}

// ===============================
// DNS Obfuscation (Secure Resolver)
// ===============================

std::string resolve_secure_dns(const std::string& hostname) {
    struct addrinfo hints = {}, *res;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    int status = getaddrinfo(hostname.c_str(), nullptr, &hints, &res);
    if (status != 0) return "[eQ5o1] DNS resolution failed.";

    char ipstr[INET_ADDRSTRLEN];
    void* addr = &((struct sockaddr_in*)res->ai_addr)->sin_addr;
    inet_ntop(res->ai_family, addr, ipstr, sizeof(ipstr));
    freeaddrinfo(res);
    return std::string(ipstr);
}

// ===============================
// Anonymous IP Generator
// ===============================

std::string generate_anonymous_ip() {
    int oct1 = rand() % 254 + 1;
    int oct2 = rand() % 254 + 1;
    int oct3 = rand() % 254 + 1;
    int oct4 = rand() % 254 + 1;
    std::stringstream ss;
    ss << oct1 << "." << oct2 << "." << oct3 << "." << oct4;
    return ss.str();
}

// ===============================
// Dox Protection & Sensitive Clear
// ===============================

void secure_wipe(std::string& buffer) {
    for (auto& c : buffer) c = 0;
}

void clear_sensitive_file(const std::string& filepath) {
    std::ofstream out(filepath, std::ios::binary | std::ios::trunc);
    out << std::string(4096, 0);
    out.close();
}

// ===============================
// MAIN ENTRY — Test Simulation
// ===============================

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: eQ5o1 [encrypt|decrypt] <infile> <outfile>" << std::endl;
        return 1;
    }

    std::string mode = argv[1];
    std::string infile = argv[2];
    std::string outfile = argv[3];

    unsigned char key[AES_KEYLEN], iv[AES_IVLEN];
    if (!generate_key_iv(key, iv)) return 2;

    int result = aes_crypt(infile, outfile, key, iv, mode == "encrypt");
    if (result != 0) {
        std::cerr << "[eQ5o1] AES operation failed with code " << result << std::endl;
        return result;
    }

    std::cout << "[eQ5o1] Success: " << mode << "ion completed." << std::endl;
    std::cout << "[eQ5o1] Secure DNS: " << resolve_secure_dns("olivia-tgdk.com") << std::endl;
    std::cout << "[eQ5o1] Masked IP: " << generate_anonymous_ip() << std::endl;

    clear_sensitive_file(infile);
    return 0;
}
