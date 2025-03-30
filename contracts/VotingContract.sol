// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingContract {
    struct Vote {
        uint256 userId;
        uint256 candidateId;
        uint256 electionId;
        uint256 timestamp;
    }

    Vote[] public votes; // Mảng để lưu trữ các phiếu bầu

    event VoteCast(uint256 userId, uint256 candidateId, uint256 electionId, uint256 timestamp); // Sự kiện khi có phiếu bầu mới

    mapping(uint256 => mapping(uint256 => bool)) public hasVoted;

    function castVote(uint256 _userId, uint256 _candidateId, uint256 _electionId) public {

        require(!hasVoted[_userId][_electionId],  unicode"Bạn đã bỏ phiếu trong cuộc bầu cử này rồi.");

        // Tạo một đối tượng Vote mới
        Vote memory newVote = Vote({
            userId: _userId,
            candidateId: _candidateId,
            electionId: _electionId,
            timestamp: block.timestamp // Lấy timestamp hiện tại của block
        });

        votes.push(newVote); // Thêm phiếu bầu vào mảng

        emit VoteCast(_userId, _candidateId, _electionId, block.timestamp); // Phát ra sự kiện VoteCast

        hasVoted[_userId][_electionId] = true;

    }

    function checkHasVoted(uint256 _userId, uint256 _electionId) public view returns (bool) {
        return hasVoted[_userId][_electionId];
    }
    
    // Hàm để lấy số lượng phiếu bầu đã được ghi nhận (cho mục đích kiểm tra)
    function getVoteCount() public view returns (uint256) {
        return votes.length;
    }

    // Hàm để lấy thông tin của một phiếu bầu cụ thể dựa trên index (cho mục đích kiểm tra)
    function getVote(uint256 index) public view returns (Vote memory) {
require(index < votes.length, unicode"Index vượt quá giới hạn");        return votes[index];
    }
}