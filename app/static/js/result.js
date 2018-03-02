$(window).on('load', function() {
    if ($("#imgbest").length) {
        var size = get_size($("#imgbest"));
        $("#image-similarity").append("相似度：100%");
        $("#image-size").append("图片尺寸：" + size.width + " × " + size.height);
    }
    $('.image-grid .image-item').each(function() {
        var img = $(this).children("img");
        var div = $(this).children("div");
        if (img.length) {
            var size = get_size(img);
            div.append("相似度：100%<br/>");
            div.append(size.width + " × " + size.height);
        }
    });
    $("body").show();
});

function get_size(img) {
    return {
        'width': img.get(0).naturalWidth,
        'height': img.get(0).naturalHeight
    };
}
