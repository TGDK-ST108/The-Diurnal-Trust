using System.Numerics;
using Microsoft.Extensions.Options;
using MilcertCoin.Api.Models;
using Nethereum.ABI.FunctionEncoding.Attributes;
using Nethereum.Contracts;
using Nethereum.RPC.Eth.DTOs;
using Nethereum.Web3;
using Nethereum.Web3.Accounts;

namespace MilcertCoin.Api.Services;

public sealed class MilcertCoinService
{
    private readonly ChainOptions _options;
    private readonly Web3 _web3;
    private readonly ContractHandler _handler;

    public MilcertCoinService(IOptions<ChainOptions> options)
    {
        _options = options.Value;

        var account = new Account(_options.OwnerPrivateKey, _options.ChainId);
        _web3 = new Web3(account, _options.RpcUrl);
        _handler = _web3.Eth.GetContractHandler(_options.ContractAddress);
    }

    public async Task<string> GetOwnerAddressAsync()
    {
        var account = await _web3.TransactionManager.Account.Address.EnsureNotNull();
        return account;
    }

    public Task<BigInteger> BalanceOfAsync(string wallet)
    {
        return _handler.QueryAsync<BalanceOfFunction, BigInteger>(
            new BalanceOfFunction { Account = wallet });
    }

    public Task<string> ApproveParticipantAsync(string wallet, bool approved)
    {
        return _handler.SendRequestAsync(
            new ApproveParticipantFunction
            {
                Account = wallet,
                Approved = approved
            });
    }

    public Task<string> SetMinterAsync(string wallet, bool allowed)
    {
        return _handler.SendRequestAsync(
            new SetMinterFunction
            {
                Account = wallet,
                Allowed = allowed
            });
    }

    public Task<string> PauseAsync()
    {
        return _handler.SendRequestAsync(new PauseFunction());
    }

    public Task<string> UnpauseAsync()
    {
        return _handler.SendRequestAsync(new UnpauseFunction());
    }

    public Task<string> MintAsync(string to, BigInteger amountWei)
    {
        return _handler.SendRequestAsync(
            new MintFunction
            {
                To = to,
                Amount = amountWei
            });
    }

    public Task<string> TransferAsync(string to, BigInteger amountWei)
    {
        return _handler.SendRequestAsync(
            new TransferFunction
            {
                To = to,
                Value = amountWei
            });
    }

    public Task<TransactionReceipt> WaitForReceiptAsync(string txHash)
    {
        return _web3.TransactionManager.TransactionReceiptService
            .PollForReceiptAsync(txHash);
    }

    private static class GuardExtensions
    {
        public static Task<string> EnsureNotNull(this string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new InvalidOperationException("Account address unavailable.");
            return Task.FromResult(value);
        }
    }

    [Function("balanceOf", "uint256")]
    public sealed class BalanceOfFunction : FunctionMessage
    {
        [Parameter("address", "account", 1)]
        public string Account { get; set; } = "";
    }

    [Function("approveParticipant")]
    public sealed class ApproveParticipantFunction : FunctionMessage
    {
        [Parameter("address", "account", 1)]
        public string Account { get; set; } = "";

        [Parameter("bool", "approved", 2)]
        public bool Approved { get; set; }
    }

    [Function("setMinter")]
    public sealed class SetMinterFunction : FunctionMessage
    {
        [Parameter("address", "account", 1)]
        public string Account { get; set; } = "";

        [Parameter("bool", "allowed", 2)]
        public bool Allowed { get; set; }
    }

    [Function("pause")]
    public sealed class PauseFunction : FunctionMessage { }

    [Function("unpause")]
    public sealed class UnpauseFunction : FunctionMessage { }

    [Function("mint")]
    public sealed class MintFunction : FunctionMessage
    {
        [Parameter("address", "to", 1)]
        public string To { get; set; } = "";

        [Parameter("uint256", "amount", 2)]
        public BigInteger Amount { get; set; }
    }

    [Function("transfer", "bool")]
    public sealed class TransferFunction : FunctionMessage
    {
        [Parameter("address", "to", 1)]
        public string To { get; set; } = "";

        [Parameter("uint256", "amount", 2)]
        public BigInteger Value { get; set; }
    }
}
