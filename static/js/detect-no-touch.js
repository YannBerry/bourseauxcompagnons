if (!("ontouchstart" in document.querySelector(".selectable-items-list"))) {
    document.querySelector(".selectable-items-list").classList.add("no-touch");
}