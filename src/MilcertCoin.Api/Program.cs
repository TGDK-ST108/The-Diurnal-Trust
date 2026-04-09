using MilcertCoin.Api.Models;
using MilcertCoin.Api.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.Configure<ChainOptions>(
    builder.Configuration.GetSection("Chain"));

builder.Services.AddSingleton<MilcertCoinService>();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.MapGet("/", () => Results.Ok(new
{
    ok = true,
    service = "MILCERTCOIN API",
    endpoints = new[]
    {
        "/api/token/balance/{wallet}",
        "/api/token/participant/approve",
        "/api/token/minter/set",
        "/api/token/pause",
        "/api/token/unpause",
        "/api/token/mint",
        "/api/token/transfer",
        "/api/token/pmz/derive",
        "/api/token/pmz/solve-for-target"
    }
}));

app.MapControllers();
app.Run();
