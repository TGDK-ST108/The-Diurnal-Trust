#pragma once
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <chrono>

enum AccessTier {
    PUBLIC = 0,
    PRIVATE = 1,
    FOREIGN = 2
};

struct TokenData {
    AccessTier tier;
    std::chrono::system_clock::time_point expiry;
    std::string dual_key;
    std::string quantum_hash;
};

class USTAF_ADL_Tokenizer {
private:
    std::unordered_map<std::string, TokenData> registry;
    std::unordered_set<std::string> revocation_list;

public:
    void register_token(const std::string& id, AccessTier tier, int lifespan_seconds, const std::string& dual_key);
    bool is_expired(const std::string& id);
    void revoke_token(const std::string& id);
    bool verify_token_hash(const std::string& id, const std::string& input_hash);
    AccessTier get_access_tier(const std::string& id, const std::string& secondary_key = "");
    void audit_view_request(const std::string& requester, const std::string& resource);
};