function bcgChange() {
    const element = document.querySelector("#bcg-change");
    const element_display = element.classList.contains("collapsed");
    if (element_display == false) {
        document.getElementById('mobile').style.backgroundImage="url(/static/img/home/background-mobile.png)";
    }
    else if (element_display == true) {
        document.getElementById('mobile').style.backgroundImage="";
    }
}