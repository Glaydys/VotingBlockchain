// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingContract {
    struct Vote {
        uint userId;
        uint candidateId;
        uint electionId;
        uint timestamp;
    }

    Vote[] public votes; // Mảng để lưu trữ các phiếu bầu

    event VoteCast(uint userId, uint candidateId, uint electionId, uint timestamp); // Sự kiện khi có phiếu bầu mới

    function castVote(uint _userId, uint _candidateId, uint _electionId) public {
        // Tạo một đối tượng Vote mới
        Vote memory newVote = Vote({
            userId: _userId,
            candidateId: _candidateId,
            electionId: _electionId,
            timestamp: block.timestamp // Lấy timestamp hiện tại của block
        });

        votes.push(newVote); // Thêm phiếu bầu vào mảng

        emit VoteCast(_userId, _candidateId, _electionId, block.timestamp); // Phát ra sự kiện VoteCast
    }

    // Hàm để lấy số lượng phiếu bầu đã được ghi nhận (cho mục đích kiểm tra)
    function getVoteCount() public view returns (uint) {
        return votes.length;
    }

    // Hàm để lấy thông tin của một phiếu bầu cụ thể dựa trên index (cho mục đích kiểm tra)
    function getVote(uint index) public view returns (Vote memory) {
require(index < votes.length, unicode"Index vượt quá giới hạn");        return votes[index];
    }
}