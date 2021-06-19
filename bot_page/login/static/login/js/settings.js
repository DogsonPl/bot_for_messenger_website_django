const referral_code = document.getElementById("referral_code")

function copy_referral_code()
{
    let copy_text_area = document.createElement("textarea")
    copy_text_area.value = referral_code.textContent
    document.body.appendChild(copy_text_area)
    copy_text_area.select()
    document.execCommand("copy")
    copy_text_area.remove()
}



$("#referral_code").tooltip({
    trigger: "click",
    placement: "top"
});

function set_tooltip(message) {
    $("#referral_code").tooltip("hide")
        .attr("data-original-title", message)
        .tooltip("show");
}

function hide_tooltip() {
    setTimeout(function() {
        $("#referral_code").tooltip("hide");
    }, 2000);
}


const clipboard = new Clipboard("span");

clipboard.on("success", function(e) {
    set_tooltip("Kod został skopiowany 😀");
    hide_tooltip();
});
