let selectedCandidate = null;

// Chọn ứng viên
function selectCandidate(id) {
    // Bỏ chọn tất cả các ứng viên trước đó
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Chọn ứng viên mới
    selectedCandidate = id;
    document.querySelectorAll('.candidate-card')[id - 1].classList.add('selected');
}

// Gửi bình chọn
function submitVote() {
    if (selectedCandidate === null) {
        alert("Vui lòng chọn một ứng viên trước khi gửi!");
        return;
    }

    // Gửi dữ liệu bình chọn lên server (giả lập)
    fetch('/submit-vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: selectedCandidate })
    })
    .then(response => response.json())
    .then(data => {
        alert("Bình chọn thành công!");
        window.location.href = "/result"; // Chuyển hướng đến trang kết quả
    })
    .catch(error => console.error("Lỗi khi gửi bình chọn:", error));
}

// Quay về trang chủ
function goHome() {
    window.location.href = "/home";
}
