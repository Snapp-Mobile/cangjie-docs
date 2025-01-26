"use strict";
(function iframePostMessage(search) {
    window.parent.postMessage({ event: "docsUrl", value: {
      href: window.location.href,
      origin: window.location.origin,
      pathname: window.location.pathname
    } }, "*");
    var h = document.body.clientHeight || 0
    h && window.parent.postMessage({
      event: "resetIframeSize",
      value: {height: h}
    },"*")
})();
