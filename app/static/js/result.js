$(window).on('load', function () {
    if ($(".image-target img").length) {
        var size = get_size($(".image-target img"));
        $(".image-info").append("<p>图片尺寸：<br>" + size.width + " × " + size.height + "</p>");
    }
    $(".image-grid .image-item").each(function () {
        var img = $(this).children("img");
        var div = $(this).children("div");
        if (img.length) {
            var size = get_size(img);
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
