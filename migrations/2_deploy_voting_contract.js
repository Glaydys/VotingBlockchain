const VotingContract = artifacts.require("VotingContract");
const ELECTION_CONTRACT_ADDRESS = "0x85CB3e967c2a07B80364a123D3a475d279e3b18c"; 

module.exports = function (deployer) {
  deployer.deploy(VotingContract, ELECTION_CONTRACT_ADDRESS);
};