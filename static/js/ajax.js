// Asynchronous GET Http request with JS
function ajaxGet(url, callback) {
    let req = new XMLHttpRequest();
    req.open("GET", url, true);
    req.addEventListener("load", function () {
        if (req.status >= 200 && req.status < 400) {
            callback(req.responseText);
        } else {
            console.error(req.status + " " + req.statusText + " (asynchronous request on " + url + ")");
        }
    });
    req.addEventListener("error", function () {
        console.error("Network error with asynchonous request on " + url);
    });
    req.send(null);
}