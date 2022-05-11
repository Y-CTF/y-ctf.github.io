// Source: https://codemyui.com/hide-header-navigation-on-scroll-down-and-show-on-scroll-up/

$(document).ready(function () {
  
    'use strict';
    
     var c, currentScrollTop = 0,
         navbar = $('nav');
  
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