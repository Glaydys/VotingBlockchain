const Web3 = require('web3');
const VotingContractJSON = require('./build/contracts/VotingContract.json'); // Đường dẫn tới ABI của contract sau khi compile

const contractAddress = "0x388852D6DCD0561C8B06D0159764CBDFb9AF2570"; // Địa chỉ contract bạn vừa deploy

const deployedContract = new web3.eth.Contract(
    VotingContractJSON.abi,
    contractAddress
);

async function interact() {
    // Kết nối đến Ganache
    const web3 = new Web3('http://127.0.0.1:7545'); // Địa chỉ RPC Server của Ganache

    // Lấy Account đầu tiên từ Ganache để làm người gọi function
    const accounts = await web3.eth.getAccounts();
    const contractOwnerAccount = accounts[0];

    // Lấy Network ID
    const networkId = await web3.eth.net.getId();

    // Lấy Contract Instance
    const deployedContract = new web3.eth.Contract(
        VotingContractJSON.abi,
        VotingContractJSON.networks[networkId].address // Địa chỉ contract đã deploy từ migration
    );

    // Thực hiện bỏ phiếu (ví dụ: user ID = 1, candidate ID = 2, election ID = 3)
    try {
        const receipt = await deployedContract.methods.castVote(1, 2, 3).send({ from: contractOwnerAccount });
        console.log('Phiếu bầu đã được ghi nhận thành công!');
        console.log('Transaction Hash:', receipt.transactionHash);

        // Lấy số lượng phiếu bầu
        const voteCount = await deployedContract.methods.getVoteCount().call();
        console.log('Tổng số phiếu bầu:', voteCount);

        // Lấy thông tin phiếu bầu đầu tiên (index 0)
        if (voteCount > 0) {
            const firstVote = await deployedContract.methods.getVote(0).call();
            console.log('Thông tin phiếu bầu đầu tiên:', firstVote);
        }

    } catch (error) {
        console.error('Lỗi khi bỏ phiếu:', error);
    }
}

interact();