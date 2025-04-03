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
    
    // Hàm để lấy số lượng phiếu bầu theo electionId
    function getVoteCount(uint256 _electionId) public view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < votes.length; i++) {
            if (votes[i].electionId == _electionId) {
                count++;
            }
        }
        return count;
    }

    // Hàm để lấy thông tin của một phiếu bầu cụ thể dựa trên index (cho mục đích kiểm tra)
    function getVote(uint256 index) public view returns (Vote memory) {
        require(index < votes.length, unicode"Index vượt quá giới hạn");        
        return votes[index];
    }

    // Hàm tổng hợp phiếu bầu theo electionId
    function getElectionResults(uint _electionId) public view returns (uint[] memory, uint[] memory) {
        // Đếm số lượng ứng viên trong cuộc bầu cử
        uint totalVotes = 0;
        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].electionId == _electionId) {
                totalVotes++;
            }
        }

        // Mảng để lưu thông tin ứng viên và số phiếu
        uint[] memory candidateIds = new uint[](totalVotes);
        uint[] memory voteCounts = new uint[](totalVotes);
        uint candidateCount = 0;

        // Duyệt qua danh sách phiếu để tổng hợp số phiếu
        for (uint i = 0; i < votes.length; i++) {
            if (votes[i].electionId == _electionId) {
                uint candidateId = votes[i].candidateId;
                bool found = false;

                // Kiểm tra xem ứng viên đã có trong danh sách chưa
                for (uint j = 0; j < candidateCount; j++) {
                    if (candidateIds[j] == candidateId) {
                        voteCounts[j]++;
                        found = true;
                        break;
                    }
                }

                // Nếu ứng viên chưa có trong danh sách, thêm mới
                if (!found) {
                    candidateIds[candidateCount] = candidateId;
                    voteCounts[candidateCount] = 1;
                    candidateCount++;
                }
            }
        }

        // Cắt bớt mảng để chỉ lấy số lượng ứng viên thực tế
        assembly {
            mstore(candidateIds, candidateCount)
            mstore(voteCounts, candidateCount)
        }

        return (candidateIds, voteCounts);
    }
}