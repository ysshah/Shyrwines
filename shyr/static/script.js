$(document).ready(function () {

    /* Autocomplete function. */
    $("#nav-search").keyup(function () {
        if ($("#nav-search").val()) {
            $.ajax({
                url: "/autocomplete/",
                type: "GET",
                data: $("form.search").serialize(),
                success: function (data) {
                    if (data) {
                        $("#auto-container").html(data);
                        $("#auto-container").show();
                    } else {
                        $("#auto-container").hide();
                    }
                }
            });
        } else {
            $("#auto-container").hide();
        }
    });

    /* Expand or contract sorting options upon arrow click. */
    // $(".sort-arrow").click(function () {
    //     var thisWindow = $(this).siblings("div.select-window.sort").get(0);
    //     if ($(this).hasClass("left")) {
    //         $(this).data("original", thisWindow.firstChild.style.marginTop);
    //         var child = $(thisWindow.children[0]);
    //         $(thisWindow).css({"height": Math.min(407, child.height()),
    //                        "overflow-y": "scroll",
    //                        "box-shadow": "0px 0px 5px #8e0606"});
    //         $(this).removeClass("left");
    //         $(this).addClass("down");
    //         child.css("margin-top", "0px");
    //     } else {
    //         $(thisWindow).css({"height": "50px",
    //                        "overflow-y": "hidden",
    //                        "box-shadow": "none"});
    //         $(thisWindow).animate({scrollTop: "0px"});
    //         $(this).removeClass("down");
    //         $(this).addClass("left");
    //         $(thisWindow.children[0]).css("margin-top", $(this).data("original"));
    //         $(this).data("clicked", false);
    //     }
    // });

    /* Expand or contract sorting options upon hover. */
    // $(".select-window.sort").hover(function () {
    //     $(this).siblings(".sort-arrow").removeClass("left");
    //     $(this).siblings(".sort-arrow").addClass("down");
    //     var child = $(this.children[0]);
    //     $(this).data("original", child.css('marginTop'));
    //     $(this).css({"height": Math.min(407, child.height()),
    //                        "overflow-y": "scroll",
    //                        "box-shadow": "0px 0px 5px #8e0606"});
    //     child.css("margin-top", "0px");
    // }, function () {
    //     $(this).siblings(".sort-arrow").removeClass("down");
    //     $(this).siblings(".sort-arrow").addClass("left");
    //     $(this).css({"height": "50px",
    //                        "overflow-y": "hidden",
    //                        "box-shadow": "none"});
    //     $(this).animate({scrollTop: "0px"});
    //     $(this.children[0]).css("margin-top", $(this).data("original"));
    // });

    /* Adds a wine to the cart from the VIEW page. */
    $('form.add').submit(function(e) {
        e.preventDefault();
        $.post('/add/', $(this).serialize(), function(data) {
            if ($(window).width() <= 900) {
                $("div#dimmer").fadeIn(function () {
                    $("div#popover-content").fadeIn().delay(1000).fadeOut(function () {
                        $("div#dimmer").fadeOut();
                    });
                });
            } else {
                $("div#popover-content").slideDown().delay(1000).slideUp();
            }
        });
    });

    /* Update a wine's quantity in the cart upon its quantity focusout. */
    $(document).on('focusout', 'div.cart-quantity form input', function() {
        $.post('/update/', $(this).parent().serialize(), function(data) {
            $('div.cart-wrapper').load('/cart-items/');
        });
    });

    /* Remove a wine bottle from the cart. */
    $(document).on('submit', 'form.remove', function(e) {
        e.preventDefault();
        $.post('/remove/', $(this).serialize(), function(data) {
            $('div.cart-wrapper').load('/cart-items/');
        });
    });

    /* Validate an email address. */
    function validate_email(passed) {
        var email = $("input#email");
        var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if (!email.val()) {
            email.css("border-color", "red");
            email.parent().css("color", "red");
            email.attr("placeholder", "Required");
            return false;
        } else if (!regex.test(email.val())) {
            $("div#form-email label").text("Invalid email address.");
            email.css("border-color", "red");
            email.parent().css("color", "red");
            return false;
        } else {
            $("div#form-email label").text("Email");
            email.parent().css("color", "black");
            email.css("border-color", "rgba(142, 6, 6, 0.5)");
            return passed;
        }
    }

    /* Validate a zipcode. Either 55555 or 55555-5555. */
    function validate_zipcode(passed) {
        var zipcode = $("input#zipcode");
        if (!zipcode.val()) {
            zipcode.css("border-color", "red");
            zipcode.parent().css("color", "red");
            zipcode.attr("placeholder", "Required");
            return false;
        } else if (!/^\d{5}(-\d{4})?$/.test(zipcode.val())) {
            $("div#form-zipcode label").text("Invalid zip.");
            zipcode.css("border-color", "red");
            zipcode.parent().css("color", "red");
            return false;
        } else {
            $("div#form-zipcode label").text("Zip Code");
            zipcode.parent().css("color", "black");
            zipcode.css("border-color", "rgba(142, 6, 6, 0.5)");
            return passed;
        }
    }

    /* Validate the order form on the cart page. */
    function validate() {
        var passed = true;
        $("input.order-form:not(input#email, input#zipcode),"
            + "select#state").each(function () {
            if (!$(this).val()) {
                $(this).css("border-color", "red");
                $(this).parent().css("color", "red");
                $(this).attr("placeholder", "Required");
                passed = false;
            }
        });
        if (!$("input#agree").prop("checked")) {
            $("div#form-agree label").css("color", "red");
            passed = false;
        }
        passed = validate_email(passed);
        passed = validate_zipcode(passed);
        return passed;
    }

    /* Change the agreement text to red or black depending on agreement. */
    $("input#agree").change(function () {
        if (!$(this).prop("checked")) {
            $("div#form-agree label").css("color", "red");
        } else {
            $("div#form-agree label").css("color", "black");
        }
    });

    /* Validate input fields upon focusout. */
    $("input.order-form:not(input#email, input#zipcode),"
        + "select#state").focusout(function () {
        if ($(this).val()) {
            $(this).parent().css("color", "black");
            $(this).css("border-color", "rgba(142, 6, 6, 0.5)");
        } else {
            $(this).css("border-color", "red");
            $(this).parent().css("color", "red");
            $(this).attr("placeholder", "Required");
        }
    });

    /* Validate email upon focusout. */
    $("input#email").focusout(function () {
        validate_email(true);
    });

    /* Validate zipcode upon focusout. */
    $("input#zipcode").focusout(function () {
        validate_zipcode(true);
    });

    /* Validate order form upon "Submit Order" button click. */
    $("button#submit-order").click(function () {
        if (validate()) {
            $.ajax({
                url: '/checkout/',
                type: "GET",
                data: $("#order-form").serialize(),
                success: function(msg) {
                    if (msg) {
                        alert(msg);
                    } else {
                        $("div#cart-content").slideUp();
                        $("form#order-form").slideUp(function () {
                            $("div#dimmer").fadeIn(function () {
                                $("div#thanks-wrapper").fadeIn();
                            });
                        });
                    }
                }
            });
        }
    });

});
