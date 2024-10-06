async function main() {
  const FraudDetection = await ethers.getContractFactory("SimpleFraudDetection");
  const fraudDetection = await FraudDetection.deploy();

  await fraudDetection.deployed();
  console.log("FraudDetection deployed to:", fraudDetection.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Error:", error);
    process.exit(1);
  });
