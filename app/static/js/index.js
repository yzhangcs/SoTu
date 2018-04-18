$(document).ready(function () {
    $("#fileimg").change(function (e) {
        var file = $(this)[0].files[0];
        if (validate_img(file))
            submit($("#imgform"));
    });

    $("#btnsubmit").click(function () {
        var url = $("#txturl").val();
        if (validate_url(url))
            submit($("#urlform"));
    });

    $(document).keypress(function (e) {
        var key = e.which;
        // 回车事件触发提交按钮
        if (key == 13) {
            e.preventDefault();
            $("#btnsubmit").click();
        }
    });

    $(".container").on({
        dragenter: function (e) {
            e.stopPropagation();
            e.preventDefault();
        },
        dragover: function (e) {
            e.stopPropagation();
            e.preventDefault();
        },
        drop: function (e) {
            e.stopPropagation();
            e.preventDefault();
            $("#dropzone").hide();
            $("#fileimg")[0].files = e.originalEvent.dataTransfer.files;
            if (validate_img($("#fileimg")[0].files[0]))
                submit($("#imgform"));
        }
    });
    $(document).on({
        dragenter: function (e) {
            e.stopPropagation();
            e.preventDefault();
            $("#dropzone").show();
        },
        dragover: function (e) {
            e.stopPropagation();
            e.preventDefault();
        },
        dragleave: function (e) {
            e.stopPropagation();
            e.preventDefault();
            if (e.clientX <= 0 ||
                e.clientX >= $(window).width() ||
                e.clientY <= 0 ||
                e.clientY >= $(window).height())
                $("#dropzone").hide();
        },
        drop: function (e) {
            e.stopPropagation();
            e.preventDefault();
            $("#dropzone").hide();
        }
    });

    $("#btnclose").click(function () {
        $("#txturl").val("");
    });
});

function validate_img(file) {
    var type = file['type'];
    if (type.split('/')[0] != 'image') {
        alert("只接受图片格式的文件");
        return false;
    }
    else if (file.size >= 3 * 1024 * 1024) {
        alert("请上传小于3M的图片");
        return false;
    }
    return true;
}

function validate_url(url) {
    var imgregex = /(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|jpeg|png|gif)/g;

    if (!url) {
        $("#txturl").addClass("warn");
        setTimeout(function () {
            $("#txturl").removeClass("warn");
        }, 2e3);
        return false;
    }
    else if (url.length > 1000) {
        alert("URL长度不超过1000");
        return false;
    }
    else if (!imgregex.test(url)) {
        alert("图片URL不合法");
        return false;
    }
    return true;
}

function submit(form) {
    $("#uploadtip").show();
    try {
        form.submit();
    }
    catch (err) {
        alert(err);
        $("#uploadtip").hide();
    }
}