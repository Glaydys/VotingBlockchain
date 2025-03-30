$(document).ready(function() {
    $.getJSON('https://esgoo.net/api-tinhthanh/1/0.htm', function(data_tinh) {        
        if (data_tinh.error === 0) {
            $.each(data_tinh.data, function(key_tinh, val_tinh) {
                $("#tinh").append(`<option value="${val_tinh.full_name}" data-id="${val_tinh.id}">${val_tinh.full_name}</option>`);
            });

            $("#tinh").change(function() {
                var tenTinh = $(this).val();
                var idTinh = $(this).find(":selected").data("id");

                $("#quan").html('<option value="0">Chọn Quận Huyện</option>');
                $("#phuong").html('<option value="0">Chọn Phường Xã</option>');
                $("#cuocBauCu").html('<option value="0">Chọn Cuộc Bầu Cử</option>');
                $(".candidate-grid").html("");

                if (idTinh) {
                    $.getJSON(`https://esgoo.net/api-tinhthanh/2/${idTinh}.htm`, function(data_quan) {
                        if (data_quan.error === 0) {
                            $.each(data_quan.data, function(key_quan, val_quan) {
                                $("#quan").append(`<option value="${val_quan.full_name}" data-id="${val_quan.id}">${val_quan.full_name}</option>`);
                            });

                            $("#quan").change(function() {
                                var tenQuan = $(this).val();
                                var idQuan = $(this).find(":selected").data("id");

                                $("#phuong").html('<option value="0">Chọn Phường Xã</option>');
                                $("#cuocBauCu").html('<option value="0">Chọn Cuộc Bầu Cử</option>');
                                $(".candidate-grid").html("");

                                if (idQuan) {
                                    $.getJSON(`https://esgoo.net/api-tinhthanh/3/${idQuan}.htm`, function(data_phuong) {
                                        if (data_phuong.error === 0) {
                                            $.each(data_phuong.data, function(key_phuong, val_phuong) {
                                                $("#phuong").append(`<option value="${val_phuong.full_name}" data-id="${val_phuong.id}">${val_phuong.full_name}</option>`);
                                            });

                                            $("#phuong").change(function() {
                                                var tenPhuong = $(this).val();
                                                var idPhuong = $(this).find(":selected").data("id");

                                                $("#cuocBauCu").html('<option value="0">Chọn Cuộc Bầu Cử</option>');
                                                $(".candidate-grid").html("");

                                                if (idPhuong) {
                                                    $.getJSON(`/get_elections?tinh=${encodeURIComponent(tenTinh)}&quan=${encodeURIComponent(tenQuan)}&phuong=${encodeURIComponent(tenPhuong)}`, function(response) {
                                                        if (response.status === "success" && response.elections.length > 0) {
                                                            $.each(response.elections, function(index, cuoc) {
                                                                $("#cuocBauCu").append(`<option value="${cuoc._id}">${cuoc.tenCuocBauCu}</option>`);
                                                            });

                                                            $("#cuocBauCu").change(function() {
                                                                var idCuocBauCu = $(this).val();
                                                                selectedElectionId = idCuocBauCu;
                                                                $(".candidate-grid").html(""); // Xóa danh sách cũ

                                                                if (idCuocBauCu) {
                                                                    $.getJSON(`/get_candidates?cuocBauCu=${idCuocBauCu}`, function(data_ungCuVien) {
                                                                        if (data_ungCuVien.status === "success" && data_ungCuVien.candidates.length > 0) {
                                                                            $.each(data_ungCuVien.candidates, function(index, ungVien) {
                                                                                console.log("Ứng viên index:", index, "ID:", ungVien.id, "Tên:", ungVien.full_name);
                                                                                // Lấy ungvien.id để thêm và xóa select - để nhất quán trong việc chọn ra ucv
                                                                                $(".candidate-grid").append(`
                                                                                    <div class="candidate-card" id="candidate-${ungVien.id}" data-candidate-id="${ungVien.id}" onclick="selectCandidate('${ungVien.id}')"> 
                                                                                        <img src="/static/images/user.png" alt="Ứng viên">
                                                                                        <p class="candidate-name">${ungVien.full_name}</p>
                                                                                    </div>
                                                                                `);
                                                                            });
                                                                        }
                                                                    });
                                                                }
                                                            });
                                                        }
                                                    });
                                                }
                                            });
                                        }
                                    });
                                }
                            });
                        }
                    });
                }
            });
        }
    });
});

let selectedCandidate = null;
let selectedCandidateId = null; 
let selectedElectionId = null;

function selectCandidate(candidateId) { 
    console.log("Hàm selectCandidate được gọi với id:", candidateId);
    $(".candidate-card").removeClass("selected");
    selectedCandidateId = candidateId; 
    console.log("selectedCandidateId: ", candidateId);
    $(`#candidate-${candidateId}`).addClass("selected"); 
}

function submitVote() {
    if (selectedCandidateId === null) {
        alert("Vui lòng chọn một ứng viên trước khi gửi!");
        return;
    }

    // **Lấy User ID và Election ID từ input (hoặc từ nơi khác trong ứng dụng của bạn)**
    const userId = $("#user_id_input").val(); // Lấy từ input ẩn
    const electionId = selectedElectionId;
    const candidateId = selectedCandidateId; // Sử dụng selectedCandidateId đã lưu

    console.log("userId:", userId); // Thêm dòng này
    console.log("candidateId:", candidateId); // Thêm dòng này
    console.log("electionId:", electionId); // Thêm dòng này
    
    if (!userId || !electionId || !candidateId) {
        alert("Thiếu thông tin User ID, Candidate ID hoặc Election ID. Vui lòng kiểm tra lại.");
        return;
    }

    const formData = new URLSearchParams();
    formData.append('userId', userId);
    formData.append('candidateId', candidateId); 
    formData.append('electionId', electionId);


    fetch('/submit_vote', { // **Sửa route thành '/submit_vote'**
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, // Gửi dữ liệu form urlencoded
        body: formData.toString()
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("Bình chọn thành công! Transaction Hash: " + data.message); // Hiển thị Transaction Hash
            window.location.href = "/result"; // Chuyển hướng đến trang kết quả
        } else if (data.status === 'error') {
            // **Xử lý lỗi từ backend, bao gồm cả lỗi "đã bỏ phiếu rồi"**
            alert("Lỗi bình chọn: " + data.message); // Hiển thị thông báo lỗi từ server (có thể là "Bạn đã bỏ phiếu trong cuộc bầu cử này rồi.")
        }
    })

    .catch(error => {
        console.error("Lỗi khi gửi bình chọn:", error);
        alert("Lỗi khi gửi bình chọn. Vui lòng thử lại sau.");
    });
}


function goHome() {
    window.location.href = "/home";
}
