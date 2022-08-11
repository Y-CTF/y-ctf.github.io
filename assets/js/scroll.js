// only on mobile (src: https://www.geeksforgeeks.org/how-to-detect-a-mobile-device-in-jquery/)
if (window.matchMedia("(max-width: 1080px)").matches) {
    // Source: https://codemyui.com/hide-header-navigation-on-scroll-down-and-show-on-scroll-up/
    $(document).ready(function () {
        'use strict';
        var c, currentScrollTop = 0;
        var navbar = $('nav');

        $(window).scroll(function () {
            var a = $(window).scrollTop();
            var b = navbar.height();

            currentScrollTop = a;

            if (c < currentScrollTop && a > b + b) {
                navbar.addClass("scrollUp");
            } else if (c > currentScrollTop && !(a <= b)) {
                navbar.removeClass("scrollUp");
            }
            c = currentScrollTop;
        });
    });
}