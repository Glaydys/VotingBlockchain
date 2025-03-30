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
                                                    // Fetch elections from backend API
                                                    $.getJSON('http://127.0.0.1:8800/get_elections', function(elections) {
                                                        if (elections && elections.length > 0) {
                                                            $.each(elections, function(index, cuoc) {
                                                                $("#cuocBauCu").append(`<option value="${cuoc.id}">${cuoc.tenCuocBauCu}</option>`);
                                                            });

                                                            $("#cuocBauCu").change(function() {
                                                                var idCuocBauCu = $(this).val();
                                                                selectedElectionId = idCuocBauCu;
                                                                $(".candidate-grid").html(""); // Clear old candidates

                                                                if (idCuocBauCu) {
                                                                    // Fetch election detail including candidates
                                                                    $.getJSON(`http://127.0.0.1:8800/get_elections/${idCuocBauCu}`, function(electionDetail) {
                                                                        if (electionDetail && electionDetail.ungCuVien && electionDetail.ungCuVien.length > 0) {
                                                                            $.each(electionDetail.ungCuVien, function(index, ungVien) {
                                                                                console.log("Ứng viên index:", index, "ID:", ungVien.id, "Tên:", ungVien.full_name);
                                                                                $(".candidate-grid").append(`
                                                                                    <div class="candidate-card" id="candidate-${ungVien.id}" data-candidate-id="${ungVien.id}" onclick="selectCandidate('${ungVien.id}')">
                                                                                        <img src="/static/images/user.png" alt="Ứng viên">
                                                                                        <p class="candidate-name">${ungVien.full_name}</p>
                                                                                    </div>
                                                                                `);
                                                                            });
                                                                        } else {
                                                                            $(".candidate-grid").html("<p>Không có ứng cử viên cho cuộc bầu cử này.</p>");
                                                                        }
                                                                    }).fail(function(jqXHR, textStatus, errorThrown) {
                                                                        console.error("Lỗi khi tải chi tiết cuộc bầu cử:", textStatus, errorThrown);
                                                                        $(".candidate-grid").html("<p>Lỗi tải ứng cử viên.</p>");
                                                                    });
                                                                }
                                                            });
                                                        } else {
                                                            $("#cuocBauCu").html('<option value="0">Không có cuộc bầu cử nào</option>');
                                                        }
                                                    }).fail(function(jqXHR, textStatus, errorThrown) {
                                                        console.error("Lỗi khi tải danh sách cuộc bầu cử:", textStatus, errorThrown);
                                                        $("#cuocBauCu").html('<option value="0">Lỗi tải cuộc bầu cử</option>');
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

    const userId = $("#user_id_input").val();
    const electionId = selectedElectionId;
    const candidateId = selectedCandidateId;

    console.log("userId:", userId);
    console.log("candidateId:", candidateId);
    console.log("electionId:", electionId);

    if (!userId || !electionId || !candidateId) {
        alert("Thiếu thông tin User ID, Candidate ID hoặc Election ID. Vui lòng kiểm tra lại.");
        return;
    }

    const formData = new URLSearchParams();
    formData.append('userId', userId);
    formData.append('candidateId', candidateId);
    formData.append('electionId', electionId);


    fetch('/submit_vote', { // **Important:** This route `/submit_vote` is not defined in your backend. You need to create it in `app.py` if you intend to use it.
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("Bình chọn thành công! Transaction Hash: " + data.message);
            window.location.href = "/result"; // You need to create a result page if you want to redirect here
        } else if (data.status === 'error') {
            alert("Lỗi bình chọn: " + data.message);
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