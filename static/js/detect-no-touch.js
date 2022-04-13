var selectableItemsListElts = document.querySelectorAll(".selectable-items-list");

if (!("ontouchstart" in selectableItemsListElts)) {
    selectableItemsListElts.forEach(function(elts) {
      elts.classList.add("no-touch");
    });
}