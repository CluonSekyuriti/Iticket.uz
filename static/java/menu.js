const icon = document.querySelector(".i")
const menu_list = document.querySelector(".menu_list")

icon.addEventListener("mouseenter", function () {
    menu_list.classList.add("active")
})
menu_list.addEventListener("mouseleave", function () {
    menu_list.classList.remove("active")
})