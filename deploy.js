# 1. start geth private node
cd geth
chmod +x start-node.sh
./start-node.sh

# 2. run the .NET API
cd ../src/MilcertCoin.Api
dotnet restore
dotnet run
